"use client"
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useEffect, useState } from "react";

interface Image {
    image_name: string;
    s3_url: string;
    uploaded_at: string;
}

const NewPage = () => {
    const [latestImage, setLatestImage] = useState<Image | null>(null);

    useEffect(() => {
        const fetchLatestImage = async () => {
            try {
                const response = await fetch("/api/latest-image");
                if (!response.ok) {
                    throw new Error("Failed to fetch latest image");
                }
                const result = await response.json();
                setLatestImage(result.image);
            } catch (error) {
                console.error(error);
            }
        };

        fetchLatestImage();
    }, []);

    return (
        <div>
            <Navbar backgroundColor="rgb(255, 255, 255)" />
            {/* 업로드된 이미지 표시 */}
            <div className="flex justify-center items-center mt-10">
                {latestImage ? (
                    <div className="text-center">
                        <img
                            src={latestImage.s3_url}
                            alt={latestImage.image_name}
                            className="w-[300px] h-[300px] object-cover rounded-lg"
                        />
                        <p className="mt-2 text-gray-600">{latestImage.image_name}</p>
                    </div>
                ) : (
                    <p>이미지가 없습니다. 업로드를 시도해주세요.</p>
                )}
            </div>
            <Footer />
        </div>
    );
}

export default NewPage;