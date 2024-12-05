"use client";
import Footer from "@/components/Footer";
import ImageUploader from "@/components/ImageUploader";
import Navbar from "@/components/Navbar";
import "./globals.css";

const Home = () => {

  return (
    <div className="bg-black">
      <div className="flex flex-col items-center">
        <Navbar backgroundColor="rgb(255, 255, 255)" />
        <img
          className="w-[350px] sm:w-[400px] md:w-[450px] lg:w-[475px] xl:w-[500px] h-auto"
          src="/images/bulb.jpg" alt="전구 이미지"
        />
        <h1 className="text-[13px] sm:text-[18px] md:text-[23px] lg:text-[28px] xl:text-[33px] 2xl:text-[38px] font-bold text-white animate-[glow_1.5s_infinite_alternate] relative text-center px-4">조명이 바뀌면 가치도 바뀝니다.</h1>
      </div>
      <div className="w-full max-w-[400px] xs:max-w-[480px] sm:max-w-[560px] md:max-w-[640px] lg:max-w-[720px] xl:max-w-[800px] mx-auto">
        <ImageUploader />
      </div>
      <Footer />
    </div>
  );
};

export default Home;
