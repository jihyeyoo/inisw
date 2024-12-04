"use client";
import Footer from "@/components/Footer";
import ImageUploader from "@/components/ImageUploader";
import Navbar from "@/components/navbar";
import { useRouter } from "next/navigation"; // useRouter 임포트
import "./globals.css";

const Home = () => {
  const handleImageUpload = async (file: File) => {
    const formData = new FormData();
    formData.append("image", file);

    try {
      // 이미지 업로드가 성공했을 때 새로운 페이지로 이동
      // 실제 서버 요청 부분을 생략했지만, 업로드 성공 후에 페이지를 이동시킵니다.
      console.log("이미지 업로드 성공");
      window.location.href = "/newpage"; // 업로드 후 /newpage로 이동
    } catch (error) {
      console.error("이미지 업로드 실패:", error);
    }
  };

  return (
    <div>
      <Navbar backgroundColor="rgb(0, 0, 0)" />
      <div id="wrapper">
        <img src="/images/bulb.jpg" alt="전구 이미지" />
        <a href="/newpage"></a>
        <h1 className="glowing-text">조명이 바뀌면 가치도 바뀝니다.</h1>
      </div>
      <ImageUploader onImageUpload={handleImageUpload} />
      <Footer />
    </div>
  );
};

export default Home;
