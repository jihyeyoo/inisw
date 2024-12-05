import { NextResponse } from "next/server";
import connectMongoDB from "@/lib/mongodb";
import Image from "@/models/Image";

export async function GET() {
    try {
        await connectMongoDB();
        // 최신 이미지 가져오기
        const latestImage = await Image.findOne().sort({ uploaded_at: -1 });

        if (!latestImage) {
            return NextResponse.json({ error: "No images found" }, { status: 404 });
        }

        return NextResponse.json({ image: latestImage }, { status: 200 });
    } catch (error) {
        console.error("Error fetching latest image:", error);
        return NextResponse.json({ error: "Failed to fetch latest image" }, { status: 500 });
    }
}
