"use client";

import React, { useState, useEffect, useRef } from "react";
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";

const ApplyBrightPage = () => {
  const [brightness, setBrightness] = useState(1.0); // 기본 밝기 값
  const [colorTemp, setColorTemp] = useState(0); // 기본 색온도 값
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const router = useRouter(); // Next.js 라우터

  // 이미지 경로
  const imagePath = "/images/interior1.png"; // 조명 적용된 인테리어 이미지
  const maskPath = "/images/mask.png"; // 주어진 마스크 이미지

  useEffect(() => {
    const loadAndProcessImage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const img = await loadImage(imagePath);
      const maskImage = await loadImage(maskPath);

      // 캔버스 크기 설정
      canvas.width = img.width;
      canvas.height = img.height;

      // 마스크 데이터 처리
      ctx.drawImage(maskImage, 0, 0);
      const maskData = ctx.getImageData(0, 0, maskImage.width, maskImage.height);

      // 밝기 및 색온도 적용
      applyAdjustments(ctx, img, maskData, brightness, colorTemp);
    };

    loadAndProcessImage();
  }, [brightness, colorTemp]);

  const loadImage = (src: string) => {
    return new Promise<HTMLImageElement>((resolve) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.src = src;
    });
  };

  const applyAdjustments = (
    ctx: CanvasRenderingContext2D,
    img: HTMLImageElement,
    maskData: ImageData,
    brightness: number,
    colorTemp: number
  ) => {
    // 원본 이미지 그리기
    ctx.drawImage(img, 0, 0);
    const imgData = ctx.getImageData(0, 0, img.width, img.height);
    const data = imgData.data;
    const mask = maskData.data;

    // 마스크 데이터에 GaussianBlur 효과 적용
    const blurredMask = applyGaussianBlur(mask, img.width, img.height);

    // 밝기 및 색온도 조정
    for (let i = 0; i < data.length; i += 4) {
      const alpha = blurredMask[i / 4] / 255; // 블러된 마스크 값을 0~1 범위로 정규화
      if (alpha > 0) { // 마스크 강도가 0.1 이상인 영역만 조정
        // 밝기 조정
        data[i] = data[i] * (1 + alpha * (brightness - 1)); // Red
        data[i + 1] = data[i + 1] * (1 + alpha * (brightness - 1)); // Green
        data[i + 2] = data[i + 2] * (1 + alpha * (brightness - 1)); // Blue

        // 색온도 조정
        data[i] += alpha * colorTemp; // Red 채널 조정
        data[i + 2] -= alpha * colorTemp; // Blue 채널 조정
      }
    }

    // 조정된 데이터를 캔버스에 업데이트
    ctx.putImageData(imgData, 0, 0);
  };

  const applyGaussianBlur = (mask: Uint8ClampedArray, width: number, height: number): Uint8ClampedArray => {
    const kernelRadius = 5; // 블러 반지름
    const kernelSize = kernelRadius * 2 + 1; // 커널 크기
    const kernel = createGaussianKernel(kernelSize, 5); // 가우시안 커널 생성
    const blurredMask = new Uint8ClampedArray(width * height);

    // 마스크 데이터에 가우시안 블러 적용
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let sum = 0;
        let weightSum = 0;
        for (let ky = -kernelRadius; ky <= kernelRadius; ky++) {
          for (let kx = -kernelRadius; kx <= kernelRadius; kx++) {
            const px = x + kx;
            const py = y + ky;
            if (px >= 0 && px < width && py >= 0 && py < height) {
              const weight = kernel[ky + kernelRadius][kx + kernelRadius]; // 올바른 인덱스 계산
              const maskValue = mask[(py * width + px) * 4]; // 마스크 Red 채널 값 사용
              sum += weight * maskValue;
              weightSum += weight;
            }
          }
        }
        blurredMask[y * width + x] = sum / weightSum; // 정규화된 블러 값
      }
    }
    return blurredMask;
  };

  const createGaussianKernel = (size: number, sigma: number): number[][] => {
    const kernel: number[][] = [];
    const radius = Math.floor(size / 2);
    let sum = 0;
    for (let x = 0; x < size; x++) {
      kernel[x] = [];
      for (let y = 0; y < size; y++) {
        const value =
          (1 / (2 * Math.PI * sigma ** 2)) *
          Math.exp(-((x - radius) ** 2 + (y - radius) ** 2) / (2 * sigma ** 2));
        kernel[x][y] = value;
        sum += value;
      }
    }
    // Normalize the kernel
    for (let x = 0; x < size; x++) {
      for (let y = 0; y < size; y++) {
        kernel[x][y] /= sum;
      }
    }
    return kernel;
  };

  const handleBrightnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBrightness(parseFloat(e.target.value));
  };

  const handleColorTempChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setColorTemp(parseInt(e.target.value, 10));
  };

  return (
    <div className="bg-black flex flex-col min-h-screen">
      <div className="flex justify-center">
        <Navbar backgroundColor="rgb(0, 0, 0)" />
      </div>
      <div className="bg-black min-h-screen flex flex-col items-center justify-center text-white">
        <div className="bg-white p-5 rounded-lg shadow-md mt-10">
          <canvas ref={canvasRef} className="rounded-md" />
          <p className="mt-3 text-gray-800 font-custom text-center">
            밝기와 색온도를 조절.
          </p>
        </div>
        <div className="mt-10 bg-gray-800 p-5 rounded-lg w-3/4 lg:w-1/2">
          <div className="mb-5">
            <label htmlFor="brightness" className="block text-lg font-custom mb-2">
              밝기: {brightness.toFixed(1)}
            </label>
            <input
              id="brightness"
              type="range"
              min="1.0"
              max="2.0"
              step="0.1"
              value={brightness}
              onChange={handleBrightnessChange}
              className="w-full accent-[#ECD77F]"
            />
          </div>
          <div>
            <label htmlFor="colorTemp" className="block text-lg font-custom mb-2">
              색온도: {colorTemp}
            </label>
            <input
              id="colorTemp"
              type="range"
              min="-50"
              max="50"
              step="1"
              value={colorTemp}
              onChange={handleColorTempChange}
              className="w-full accent-[#ECD77F]"
            />
          </div>
        </div>
        <button
          onClick={() => router.push("/selectloc")}
          className="group mt-5 mb-10 bg-gray-700 px-5 py-2 rounded-lg hover:bg-[#ECD77F]"
        >
          <p className="text-white font-second group-hover:text-black">다른 조명 적용하기</p>
        </button>
      </div>
      <Footer />
    </div>
  );
};

export default ApplyBrightPage;
