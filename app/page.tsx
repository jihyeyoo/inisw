"use client";
import Footer from "@/components/Footer";
import ImageUploader from "@/components/ImageUploader";
import Navbar from "@/components/Navbar";
import "./globals.css";

const Home = () => {

  return (
    <div className="bg-black">
      <div className="flex flex-col items-center">
        <Navbar backgroundColor="rgb(0, 0, 0)" />
        <img
          className="w-[350px] sm:w-[400px] md:w-[450px] lg:w-[475px] xl:w-[500px] h-auto"
          src="/images/bulb.jpg" alt="전구 이미지"
        />
        <span className="font-second text-gray-700 text-[27px] animate-[glow_1.2s_infinite_alternate]">
        조명이 바뀌면 가치도 바뀝니다.
          </span>
        </div>
      <div className="w-full max-w-[400px] xs:max-w-[480px] sm:max-w-[560px] md:max-w-[640px] lg:max-w-[720px] xl:max-w-[800px] mx-auto">
        <ImageUploader />
      </div>
      <Footer />
    </div>
  );
};

export default Home;
