"use client";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Image {
    image_name: string;
    s3_url: string;
    uploaded_at: string;
}

const NewPage = () => {
    const [latestImage, setLatestImage] = useState<Image | null>(null);
    const router = useRouter();

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

    const handleViewRecommendation = () => {
        // 임의 좌표 설정
        const coordinates = { x: 185, y: 185 };

        // 이미지 URL과 좌표를 쿼리 문자열로 생성
        const query = new URLSearchParams({
            imageUrl: latestImage?.s3_url || "",
            x: coordinates.x.toString(),
            y: coordinates.y.toString(),
        }).toString();

        // 문자열 형태로 이동
        router.push(`/location?${query}`);
    };

    return (
        <div className="bg-black flex flex-col min-h-screen">
            {/* Navbar */}
            <div className="flex justify-center">
                <Navbar backgroundColor="rgb(0, 0, 0)" />
            </div>

            {/* Content */}
            <div className="flex flex-grow justify-center items-center mt-10">
                {latestImage ? (
                    <div className="mb-20 bg-white rounded-lg shadow-md p-6 text-center w-[320px]">
                        <img
                            src={latestImage.s3_url}
                            alt={latestImage.image_name}
                            className="w-full h-[300px] object-cover rounded-md"
                        />
                        <p className="mt-3 text-gray-800 font-custom">
                            업로드된 이미지
                        </p>
                        {/* 추천 위치 보기 버튼 */}
                        <button
                            onClick={handleViewRecommendation}
                            className="group mt-5 bg-gray-700 px-5 py-2 rounded-lg hover:bg-[#ECD77F]"
                        >
                            <p className="text-white font-second group-hover:text-black">
                                추천 위치 보기
                            </p>
                        </button>
                    </div>
                ) : (
                    <p className="text-white">이미지가 없습니다. 업로드를 시도해주세요.</p>
                )}
            </div>

            {/* Footer */}
            <Footer className="w-full bg-black text-white p-4 text-center" />
        </div>
    );
};

export default NewPage;
