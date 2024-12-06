"use client";
import { useState } from "react";
import { useRouter } from "next/navigation"; // useRouter 추가
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const SelectLocPage = () => {
    const lights = [
        { id: 1, src: "/images/light1.jpg", appliedSrc: "/images/interior1.png" },
        { id: 2, src: "/images/light2.png", appliedSrc: "/images/interior2.png" },
    ];

    const [currentLightIndex, setCurrentLightIndex] = useState(0);
    const currentLight = lights[currentLightIndex];

    const router = useRouter(); // Next.js 라우터

    const handleNextLight = () => {
        setCurrentLightIndex((prevIndex) => (prevIndex + 1) % lights.length);
    };

    const handlePrevLight = () => {
        setCurrentLightIndex((prevIndex) =>
            prevIndex === 0 ? lights.length - 1 : prevIndex - 1
        );
    };

    const handleApplyBright = () => {
        router.push("/applybright"); // applybright 페이지로 이동
    };

    return (
        <div className="bg-black flex flex-col min-h-screen">
            {/* Navbar */}
            <div className="flex justify-center">
                <Navbar backgroundColor="rgb(0, 0, 0)" />
            </div>

            {/* Content */}
            <div className="flex flex-grow justify-center items-center mt-10 mb-20 space-x-10">
                {/* 조명 이미지 박스 */}
                <div className="bg-white rounded-lg shadow-md p-4 text-center w-[150px] h-[150px] relative">
                    <button
                        onClick={handlePrevLight}
                        className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-500 font-custom rounded-full w-8 h-8 flex justify-center items-center hover:bg-gray-400"
                        aria-label="Previous Light"
                    >
                        &lt;
                    </button>
                    <img
                        src={currentLight.src}
                        alt="Light Image"
                        className="w-full h-full object-contain rounded-md"
                    />
                    <button
                        onClick={handleNextLight}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 font-custom rounded-full w-8 h-8 flex justify-center items-center hover:bg-gray-400"
                        aria-label="Next Light"
                    >
                        &gt;
                    </button>
                </div>

                {/* 메인 이미지 박스 */}
                <div className="bg-white rounded-lg shadow-md p-5 text-center w-[320px] relative">
                    <img
                        src={currentLight.appliedSrc}
                        alt="Applied Interior"
                        className="w-full h-[300px] object-cover rounded-md"
                    />
                    {/* Apply Bright 버튼 */}
                    <button
                        onClick={handleApplyBright}
                        className="group mt-4 bg-gray-700 px-5 py-2 rounded-lg hover:bg-[#ECD77F]"
                    >
                        <p className="text-white font-second group-hover:text-black">
                            Apply Bright
                        </p>
                    </button>
                </div>
            </div>
            <Footer className="w-full bg-black text-white p-4 text-center" />
        </div>
    );
};

export default SelectLocPage;
