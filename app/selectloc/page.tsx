"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation"; // useRouter 추가
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

// 'imageSrc'와 'appliedSrc'를 갖는 객체 배열 타입을 정의
interface Light {
  imageSrc: string;
  appliedSrc: string;
  maskPath: string;
}

const SelectLocPage = () => {
  // latestLight의 타입을 명시적으로 설정
  const [latestLight, setLatestLight] = useState<Light[] | null>(null);
  const [currentLightIndex, setCurrentLightIndex] = useState(0); // 이미지 인덱스를 관리
  const router = useRouter(); // Next.js 라우터

  useEffect(() => {
    // MongoDB에서 최신 데이터 가져오기
    const fetchLatestData = async () => {
      const response = await fetch("/api/latest-image"); // API 호출
      const data = await response.json();

      // 응답 데이터를 로그로 출력해서 확인하기
      console.log(data);

      const imageName = data.image.s3_url;  // image_name을 data.image에서 가져오기
      const fileName = imageName.split('-').slice(-1)[0];
      const resFileName = imageName.split('/').pop().replace('.png', '');

      const lampCount = 3;  // 예시로 lamp1, lamp2, lamp3을 사용할 것

      // 이미지 URL 생성
      const lights = Array.from({ length: lampCount }, (_, index) => {
        const lampIndex = index + 1;
        const imageSrc = `https://lumterior.s3.ap-northeast-2.amazonaws.com/lamp/lamp${lampIndex}.png`;
        const appliedSrc = `https://lumterior.s3.ap-northeast-2.amazonaws.com/.%5Clamp${lampIndex}_results/${fileName}-diffusion-results/results/${resFileName}_temp_321.png`;
        // 마스크 이미지 경로 생성
        const maskPath = `https://lumterior.s3.ap-northeast-2.amazonaws.com/.%5Clamp${lampIndex}_results/${fileName}-diffusion-results/lamp${lampIndex}_results/mask_${resFileName}_temp_321.png`;

        return { imageSrc, appliedSrc, maskPath }; // maskPath 추가
      });

      setLatestLight(lights);  // lights 배열을 상태로 저장
    };

    fetchLatestData();
  }, []);

  // Next 버튼 클릭 시
  const handleNextLight = () => {
    if (latestLight) {
      setCurrentLightIndex((prevIndex) => (prevIndex + 1) % latestLight.length); // 최신 데이터 배열 길이로 인덱스 변경
    }
  };

  // Previous 버튼 클릭 시
  const handlePrevLight = () => {
    if (latestLight) {
      setCurrentLightIndex((prevIndex) =>
        prevIndex === 0 ? latestLight.length - 1 : prevIndex - 1 // 인덱스를 순환하도록 처리
      );
    }
  };

  const handleApplyBright = () => {
    if (latestLight) {
      const currentLight = latestLight[currentLightIndex];
      const imagePath = currentLight.appliedSrc;
      const maskPath = currentLight.maskPath; // maskPath를 가져옴

      router.push(`/applybright?imagePath=${encodeURIComponent(imagePath)}&maskPath=${encodeURIComponent(maskPath)}`);
    }
  };

  // 데이터가 로드되지 않았을 때 로딩 화면 표시
  if (!latestLight) {
    return <div>Loading...</div>;
  }

  return (
    <div className="bg-black flex flex-col min-h-screen">
      <div className="flex justify-center">
        <Navbar backgroundColor="rgb(0, 0, 0)" />
      </div>

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
            src={latestLight[currentLightIndex].imageSrc}
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
            src={latestLight[currentLightIndex].appliedSrc}
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
      <Footer />
    </div>
  );
};

export default SelectLocPage;