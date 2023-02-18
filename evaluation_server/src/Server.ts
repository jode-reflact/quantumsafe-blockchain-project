import express, { Request, Response } from 'express';
import { Collection, Db, MongoClient } from 'mongodb';
import bodyParser from 'body-parser';

export type TestResult = any;

export class EvaluationServer {
    public app = express();
    public mainDb: Db
    public testResultsCol: Collection<TestResult>

    constructor() {
        console.log('start Up')
        this.initDB()
        this.initExpress()
    }
    private async initDB() {
        const mongoClient = await MongoClient.connect("mongodb://" + process.env.dbuser + ":" + process.env.dbpass + "@localhost:27017/admin");
        console.log('mongoConnection', mongoClient)
        this.mainDb = mongoClient.db(process.env.dbname);
        this.testResultsCol = this.mainDb.collection("testResults");
    }
    private async initExpress() {
        this.app.use(bodyParser.json({ limit: "100mb" }));
        await this.app.listen(80)

        this.app.post("/completed_test", [], async (req: Request, res: Response) => {
            const testResult: TestResult = req.body;
            await this.testResultsCol.insertOne(testResult);
            // TODO: end test
        })
        this.app.get("*", [], (req: Request, res: Response) => {
            res.json('works')
        });
    }
}