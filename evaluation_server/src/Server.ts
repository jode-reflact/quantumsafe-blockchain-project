import express, { Request, Response } from 'express';
import { Collection, Db, MongoClient } from 'mongodb';
import bodyParser from 'body-parser';
import Docker from 'dockerode';
import path from 'path'
import { spawn } from 'child_process'

export type TestResult = any;

export class EvaluationServer {
    public app = express();
    public mainDb: Db
    public testResultsCol: Collection<TestResult>
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
    }
    private async initExpress() {
        this.app.use(bodyParser.json({ limit: "100mb" }));
        await this.app.listen(80)

        this.app.post("/completed_test", [], async (req: Request, res: Response) => {
            const testResult: TestResult = req.body;
            await this.testResultsCol.insertOne(testResult);
            res.json('inserted')
            // TODO: end test
        })
        this.app.get("*", [], (req: Request, res: Response) => {
            res.json('works')
        });
    }
    private async initLocalDocker() {
        this.docker = new Docker()
        this.docker.listContainers((err, containers) => {
            console.log('works');
            console.log('containers', containers)
        });
        this.runLocalTestRunnerScript()
    }
    private async runLocalTestRunnerScript() {
        const p = path.resolve('../../docker-runner.py')
        const process = spawn('python', [p]);
        process.stdout.on('data', (data) => {
            console.log('Python Data:', data)
        });
    }
}