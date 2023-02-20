import express, { Request, Response } from 'express';
import { Collection, Db, MongoClient } from 'mongodb';
import bodyParser from 'body-parser';
import Docker from 'dockerode';
import path from 'path'
import { spawn } from 'child_process'
import { setTimeout } from "timers/promises";

export type TestResult = {
    CIPHER: Cipher,
    TEST_ID: string,
    TEST_DATE: string,
    TEST_TRANSACTION_COUNT: number,
    TEST_NODE_COUNT: number,
    TEST_CLIENT_COUNT: number,
    CHAIN: { index: number, blocks: any[] }
};

export type TestConfig = { cipher: Cipher, n_transactions: number };

export type Cipher = 'dilithium' | 'ecc' | 'rsa'
const allCipher: Cipher[] = ['dilithium', 'ecc', 'rsa']
const allTransactionCounts = [1000]

export class EvaluationServer {
    public app = express();
    public mainDb: Db
    public testResultsCol: Collection<TestResult>
    public scheduledTestsCol: Collection<TestConfig>
    public docker: Docker;

    constructor() {
        console.log('start Up')
        this.initDB()
        this.initExpress()
        this.initLocalDocker()
    }
    private async initDB() {
        const mongoClient = await MongoClient.connect("mongodb://" + process.env.dbuser + ":" + process.env.dbpass + "@127.0.0.1:27017/admin");
        this.mainDb = mongoClient.db(process.env.dbname);
        this.testResultsCol = this.mainDb.collection("testResults");
        this.scheduledTestsCol = this.mainDb.collection("scheduledTests");
        await this.setupDb();
    }
    private async setupDb() {
        const scheduledTestCount = await this.scheduledTestsCol.countDocuments();
        if (scheduledTestCount == 0) {
            const tests: TestConfig[] = []
            for (const cipher of allCipher) {
                for (const n_transactions of allTransactionCounts) {
                    for (let i = 0; i < 10; i++) {
                        const config: TestConfig = { cipher, n_transactions }
                        tests.push(config)
                    }
                }
            }
            await this.scheduledTestsCol.insertMany(tests);
        }
        this.runNextTest()
    }
    private async initExpress() {
        this.app.use(bodyParser.json({ limit: "100mb" }));
        await this.app.listen(80)

        this.app.post("/completed_test", [], async (req: Request, res: Response) => {
            const testResult: TestResult = req.body;
            console.log('test Completed', testResult)
            await this.testResultsCol.insertOne(testResult);
            await this.scheduledTestsCol.deleteOne({ cipher: testResult.CIPHER, n_transactions: testResult.TEST_TRANSACTION_COUNT });
            this.stopLocalTest();
            await setTimeout(120000) // wait 2 minutes
            this.runNextTest();
            res.json('inserted')
        })
        this.app.get("*", [], (req: Request, res: Response) => {
            res.json('works')
        });
    }
    private async initLocalDocker() {
        this.docker = new Docker()
    }
    private async runNextTest() {
        const nextConfig = await this.scheduledTestsCol.findOne();
        console.log('runningNextTest', nextConfig);
        this.runLocalTestRunnerScript(nextConfig);
    }
    private async runLocalTestRunnerScript(config: TestConfig) {
        const p = path.resolve('../docker-runner.py')
        console.log('python path', p)
        const process = spawn('python', [p, config.cipher, config.n_transactions + ""]);
        process.stdout.on('data', (data) => {
            console.log('Python Data:', data.toString())
        });
    }
    private async stopLocalTest() {
        try {
            this.docker.listContainers((err, containers) => {
                console.log('stopping all Containers');
                containers.forEach((containerInfo) => {
                    this.docker.getContainer(containerInfo.Id).remove({ force: true });
                });
            });
        } catch (error) {
            console.error('Error on stopping local test', error);
        }
    }
}