// app/api/location-coordinates/route.ts
import { NextResponse } from "next/server";
import connectMongoDB from "@/lib/mongodb";
import Image from "@/models/Image";

export async function GET() {
    try {
        // 데이터베이스 연결
        await connectMongoDB();

        // 모든 이미지의 마스크 좌표 조회
        const images = await Image.find({}, {
            image_name: 1,
            s3_url: 1,
            'mask_images.cluster_center': 1,
            'mask_images.cluster_id': 1,
            'mask_images.mask_img_1': 1,
            'mask_images.mask_img_2': 1,
            'mask_images.mask_img_3': 1
        });

        if (!images || images.length === 0) {
            return NextResponse.json({ error: "No images found" }, { status: 404 });
        }

        return NextResponse.json({ images }, { status: 200 });
    } catch (error) {
        console.error("Error fetching image data:", error);
        return NextResponse.json({ error: "Failed to fetch image data" }, { status: 500 });
    }
}