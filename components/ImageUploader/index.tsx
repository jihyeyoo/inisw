"use client";
import { useState } from "react";

interface ImageUploaderProps {
  onImageUpload: (imageInfo: { name: string, url: string }) => void;
}

const ImageUploader = ({ onImageUpload }: ImageUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      alert("이미지 파일만 업로드 가능합니다.");
      return;
    }

    try {
      // FormData 생성
      const formData = new FormData();
      formData.append('file', file);

      // 서버에 업로드 요청
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        // 부모 컴포넌트에 이미지 정보 전달 (선택적)
        if (onImageUpload) {
          onImageUpload({
            name: result.image.name,
            url: result.image.url
          });
        }
        
        // NewPage로 이동 (컴포넌트라서 라우터 사용 불가능해서 이런 식으로 구성)
        window.location.href = "/newpage";
      } else {
        alert(result.error || '업로드 중 오류가 발생했습니다.');
      }
    } catch (error) {
      console.error("이미지 업로드 중 오류:", error);
      alert('이미지 업로드에 실패했습니다.');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  return (
    <div className="relative w-full h-[45vh] flex justify-center items-center">
      {/* 드래그 앤 드롭 영역 */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`w-[400px] h-[150px] flex justify-center items-center bg-gray-100 rounded-lg p-5 cursor-pointer ${isDragging ? "border-2 border-dashed border-black" : "border-2 border-dashed border-gray-400"
          }`}
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
          id="fileInput"
        />
        <label
          htmlFor="fileInput"
          className="cursor-pointer flex flex-col justify-center items-center text-center"
        >
          <span className="font-custom text-gray-700 text-[17px]">
            인테리어 이미지를 업로드하세요.
          </span>
          <img
            src="/images/upload.png"
            alt="업로드 아이콘"
            className="w-[55px] h-[48px] mt-2"
          />
        </label>
      </div>

      {/* 이미지 미리보기 */}
      {/* {preview && (
        <div className="absolute top-4 left-4 w-[100px] h-[100px]">
          <img
            src={preview}
            alt="미리보기"
            className="w-full h-full object-cover rounded-md"
          />
        </div>
      )} */}
    </div>
  );
};

export default ImageUploader;
