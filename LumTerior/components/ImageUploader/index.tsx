import { useState } from "react";

interface ImageUploaderProps {
  onImageUpload: (file: File) => Promise<void>; // onImageUpload 속성 정의
}

const ImageUploader = ({ onImageUpload }: ImageUploaderProps) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // 이미지를 읽고 resize
  const resizeImage = (file: File, maxWidth: number, maxHeight: number): Promise<string> => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const reader = new FileReader();

      reader.onload = () => {
        img.src = reader.result as string;
      };

      img.onload = () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        if (!ctx) {
          reject("Canvas context could not be created");
          return;
        }

        // 이미지가 등록되는 캔버스 512x512 resize
        canvas.width = maxWidth;
        canvas.height = maxHeight;

        // resize된 이미지 그리기
        ctx.drawImage(img, 0, 0, maxWidth, maxHeight);

        // 캔버스를 데이터 URL로 변환
        const resizedDataUrl = canvas.toDataURL("image/png");
        resolve(resizedDataUrl);
      };

      img.onerror = (error) => {
        reject(error);
      };

      reader.onerror = (error) => {
        reject(error);
      };

      reader.readAsDataURL(file);
    });
  };

  const handleFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      alert("이미지 파일만 업로드 가능합니다.");
      return;
    }

    try {
      const resizedImage = await resizeImage(file, 512, 512);
      setPreview(resizedImage);
      await onImageUpload(file); // 부모 컴포넌트로 업로드된 이미지 전달
    } catch (error) {
      console.error("이미지를 리사이즈하는 중 오류가 발생했습니다:", error);
    }
  };

  // 파일 선택 이벤트
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  // 드래그 앤 드롭 이벤트 처리
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
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '85vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {/* 이미지 업로드 박스     border: isDragging ? '2px dashed black' : '2px dashed gray',*/}
      
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          width: '400px', // 고정된 너비
          height: '150px', // 고정된 높이
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor:'rgb(250, 250, 250)' , // 박스 내부 배경색 설정
          borderRadius: '10px', 
          padding: '20px',
          cursor: 'pointer', 
        }}
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="fileInput"
        />
        <label htmlFor="fileInput" style={{ cursor: "pointer", textAlign: 'center' }}>
        <span
            style={{
              fontFamily: 'Pretendard-Bold, sans-serif', // 폰트 설정 
              color: '#333', 
              fontSize: '16px', 
            }}
          >
            인테리어 이미지를 업로드하세요.
          </span>
          <img
            src="/images/upload.png"
            alt="업로드 아이콘"
            style={{ width: '55px', height: '48px', marginLeft: '78px'}}
          />
          
        </label>
      </div>
    </div>
  );
};

export default ImageUploader;