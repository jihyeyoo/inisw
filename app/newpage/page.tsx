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

    const handleViewRecommendation = async () => {
        try {
            // Step 1: Flask 서버 호출
            const flaskResponse = await fetch("http://localhost:8000/run-higan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });

            if (!flaskResponse.ok) {
                const error = await flaskResponse.json();
                console.error("Flask 서버 호출 실패:", error.error || "알 수 없는 오류");
                alert("추천 위치 분석에 실패했습니다.");
                return;
            }

            const flaskData = await flaskResponse.json();
            console.log("Flask 실행 결과:", flaskData);

            // Step 2: 기존 좌표 및 쿼리 생성 로직
            const coordinates = { x: 210, y: 145 }; // 임의 좌표
            const query = new URLSearchParams({
                imageUrl: latestImage?.s3_url || "",
                x: coordinates.x.toString(),
                y: coordinates.y.toString(),
            }).toString();

            // Step 3: 기존 URL 이동 로직
            router.push(`/location?${query}`);
        } catch (error) {
            console.error("추천 위치 보기 처리 실패:", error);
            alert("추천 위치 처리가 실패했습니다.");
        }
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
            <Footer />
        </div>
    );
};

export default NewPage;
