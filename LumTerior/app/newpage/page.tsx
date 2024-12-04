"use client";

import Navbar from "@/components/navbar";
import Footer from "@/components/Footer";
import "../globals.css";

const NewPage = () => {
  return (
    <div>
      <Navbar backgroundColor="rgb(0, 0, 0)" />
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        {/* 흰색 박스 */}
        <div
          style={{
            backgroundColor: '#ffffff', // 흰색 배경
            borderRadius: '10px', // 모서리를 둥글게
            padding: '20px',
            boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.2)',
            textAlign: 'center',
            maxWidth: '400px', // 박스 최대 너비 설정
          }}
        >
          {/* 업로드된 이미지 */}
          <img
            src="/images/bg0101.png" // images 폴더 내의 이미지
            alt="조명 위치 추천 이미지"
            style={{
              width: '100%',
              height: 'auto',
              borderRadius: '10px', // 이미지의 모서리도 둥글게
              marginBottom: '17px', // 이미지와 텍스트 사이의 간격
            }}
          />
          {/* 이미지 설명 텍스트 */}
          <p
            style={{
              color: '#333',
              fontSize: '18px',
              fontFamily: 'Pretendard-Bold, sans-serif', // 폰트 설정
            }}
          >
            조명 위치를 선택하세요.
          </p>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default NewPage;
