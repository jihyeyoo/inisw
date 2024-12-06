"use client";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useSearchParams, useRouter } from "next/navigation";

const LocationPage = () => {
    const searchParams = useSearchParams();
    const router = useRouter();

    // 이미지와 좌표를 쿼리로 받음
    const imageUrl = searchParams.get("imageUrl");
    const x = parseInt(searchParams.get("x") || "0", 10);
    const y = parseInt(searchParams.get("y") || "0", 10);

    const handleIconClick = () => {
        // 이동할 경로 설정
        router.push("/selectloc");
    };

    return (
        <div className="bg-black flex flex-col min-h-screen">
            {/* Navbar */}
            <div className="flex justify-center">
                <Navbar backgroundColor="rgb(0, 0, 0)" />
            </div>

            {/* Content */}
            <div className="flex flex-grow justify-center items-center mt-10">
                <div className="bg-white rounded-lg shadow-md p-6 text-center w-[320px] relative">
                    {/* 이미지 */}
                    <div className="relative w-full h-[300px]">
                        <img
                            src={imageUrl || "/placeholder.jpg"} // 기본값으로 placeholder 설정
                            alt="Uploaded"
                            className="w-full h-full object-cover rounded-md"
                        />
                        {/* 아이콘 */}
                        <img
                            src="/images/loc.png"
                            alt="Location Icon"
                            className="absolute cursor-pointer"
                            style={{
                                top: y,
                                left: x,
                                width: "35px",
                                height: "35px",
                            }}
                            onClick={handleIconClick} // 아이콘 클릭 핸들러
                        />
                    </div>
                    {/* 텍스트 + 아이콘 */}
                    <div className="flex items-center justify-center mt-5 space-x-2">
                        <p className="text-gray-800 font-custom">위치를 선택하세요</p>
                        <img
                            src="/images/loc.png"
                            alt="Location Icon"
                            className="w-5 h-5"
                        />
                    </div>
                </div>
            </div>

            {/* Footer */}
            <Footer className="w-full bg-black text-white p-4 text-center" />
        </div>
    );
};

export default LocationPage;
