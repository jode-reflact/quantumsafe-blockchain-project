import express, { Request, Response } from 'express';
import { Collection, Db, MongoClient, ObjectId } from 'mongodb';
import bodyParser from 'body-parser';
import Docker from 'dockerode';
import path from 'path'
import { spawn } from 'child_process'
import { setTimeout } from "timers/promises";

export type Transaction = {
    amount: string,
    receivedAt: string,
    receiver: string,
    sender: string,
    signature: string,
    timestamp: string,
};
export type Block = {
    index: number,
    nonce: number,
    previous_hash: string,
    timestamp: string,
    transactions: Transaction[]
}

export type TestResult = {
    CIPHER: Cipher,
    TEST_ID: string,
    TEST_DATE: string,
    TEST_TRANSACTION_COUNT: number,
    TEST_NODE_COUNT: number,
    TEST_CLIENT_COUNT: number,
    USE_CACHE: boolean,
    BLOCK_SIZE: number,
    CHAIN: { index: number, blocks: Block[], ids?: ObjectId[] }
};

export type TestConfig = {
    cipher: Cipher,
    n_transactions: number,
    use_cache: boolean,
    block_size: number
};

export type Cipher = 'dilithium' | 'ecc' | 'rsa'
const allCipher: Cipher[] = ['dilithium', 'ecc', 'rsa']
//const allTransactionCounts = [100, 500, 1000, 2000]
const allTransactionCounts = [1000]
const allBlockSizes = [59, 69]

const use_cache = true;

export class EvaluationServer {
    public app = express();
    public mainDb: Db
    public testResultsCol: Collection<TestResult>
    public scheduledTestsCol: Collection<TestConfig>
    public blocksCol: Collection<Block>
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
        this.blocksCol = this.mainDb.collection("blocks");
        await this.setupDb();
    }
    private async setupDb() {
        const scheduledTestCount = await this.scheduledTestsCol.countDocuments();
        if (scheduledTestCount == 0) {
            const tests: TestConfig[] = []
            for (const cipher of allCipher) {
                for (const n_transactions of allTransactionCounts) {
                    for (const block_size of allBlockSizes) {
                        for (let i = 0; i < 10; i++) {
                            const config: TestConfig = { cipher, n_transactions, use_cache, block_size }
                            tests.push(config)
                        }
                    }
                }
            }
            await this.scheduledTestsCol.insertMany(tests);
        }
        const testRunning = await this.isTestRunning()
        if (!testRunning) {
            this.runNextTest()
        }
    }
    private async initExpress() {
        this.app.use(bodyParser.json({ limit: "500mb" }));
        await this.app.listen(80)

        this.app.post("/completed_test", [], async (req: Request, res: Response) => {
            const testResult: TestResult = req.body;
            console.log('test Completed', testResult.USE_CACHE)
            console.log('Bool Type', typeof (testResult.USE_CACHE))
            const result = await this.blocksCol.insertMany(testResult.CHAIN.blocks);
            const ids: ObjectId[] = Object.values(result.insertedIds);
            testResult.CHAIN.blocks = [];
            testResult.CHAIN.ids = ids;
            await this.testResultsCol.insertOne(testResult);
            await this.scheduledTestsCol.deleteOne({ cipher: testResult.CIPHER, n_transactions: testResult.TEST_TRANSACTION_COUNT, use_cache: testResult.USE_CACHE, block_size: testResult.BLOCK_SIZE });
            this.stopLocalTest();
            await setTimeout(120000) // wait 2 minutes
            this.runNextTest();
            res.json('inserted');
        })
        this.app.post("/log_error", [], (req: Request, res: Response) => {
            const body = req.body;
            console.log('Error from node:' + req.ip, body.error);
            res.json('logged');
        });
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
        if (nextConfig != null) {
            this.runLocalTestRunnerScript(nextConfig);
        } else {
            this.setupDb();
        }

    }
    private async runLocalTestRunnerScript(config: TestConfig) {
        const p = path.resolve('../docker-runner.py')
        const process = spawn('python', [p, config.cipher, config.n_transactions + "", config.use_cache + "", config.block_size + ""]);
        /*
        process.stdout.on('data', (data) => {
            console.log('Python Data:', data.toString())
        });
        */
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
    private async isTestRunning() {
        return new Promise<boolean>((resolve, reject) => {
            try {
                this.docker.listContainers((err, containers) => {
                    resolve(containers.length > 0)
                });
            } catch (error) {
                resolve(false)
            }
        })
    }
}