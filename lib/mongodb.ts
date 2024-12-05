import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI;

if (!MONGODB_URI) {
    throw new Error('Please define the MONGODB_URI environment variable inside .env.local');
}

interface MongooseCache {
    conn: mongoose.Connection | null;
    promise: Promise<mongoose.Mongoose> | null;
}

declare global {
    var mongoose: MongooseCache | undefined;
}

let cached = global.mongoose;

if (!cached) {
    cached = global.mongoose = { conn: null, promise: null };
}

async function connectMongoDB() {
    if (cached!.conn) {
        return cached!.conn;
    }

    if (!cached!.promise) {
        const opts = {
            bufferCommands: false,
            dbName:'lumterior', // DB 이름 설정
        };

        cached!.promise = mongoose.connect(MONGODB_URI!, opts).then((mongooseInstance) => {
            cached!.conn = mongooseInstance.connection;
            return mongooseInstance;
        });
    }

    try {
        const mongooseInstance = await cached!.promise;
        return cached!.conn;
    } catch (e) {
        cached!.promise = null;
        throw e;
    }
}

export default connectMongoDB;