"use client";
import React, { useState, useEffect, useRef } from "react";

const ApplyBrightPage = () => {
  const [brightness, setBrightness] = useState(1.0); // 기본 밝기 값
  const [colorTemp, setColorTemp] = useState(0); // 기본 색온도 값
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // 이미지 경로
  const imageAPath = "/images/interior1.png"; // 조명 적용된 인테리어 이미지
  const imageBPath = "/images/bg04.png"; // 초기 사용자 입력 이미지

  useEffect(() => {
    const loadAndProcessImages = async () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      // 이미지 로드
      const imgA = await loadImage(imageAPath);
      const imgB = await loadImage(imageBPath);

      // 캔버스 크기 설정
      canvas.width = imgA.width;
      canvas.height = imgA.height;

      // SSIM 기반 마스크 생성
      const mask = generateMask(imgA, imgB, ctx);

      // 밝기 및 색온도 초기 적용
      applyAdjustments(ctx, imgA, mask, brightness, colorTemp);
    };

    loadAndProcessImages();
  }, [brightness, colorTemp]);

  const loadImage = (src: string): Promise<HTMLImageElement> =>
    new Promise((resolve) => {
      const img = new Image();
      img.src = src;
      img.onload = () => resolve(img);
    });

  const generateMask = (
    imgA: HTMLImageElement,
    imgB: HTMLImageElement,
    ctx: CanvasRenderingContext2D
  ): Uint8ClampedArray => {
    // 이미지 A 처리
    ctx.drawImage(imgA, 0, 0);
    const imgAData = ctx.getImageData(0, 0, imgA.width, imgA.height);

    // 이미지 B 처리
    ctx.drawImage(imgB, 0, 0);
    const imgBData = ctx.getImageData(0, 0, imgB.width, imgB.height);

    // 차이 마스크 생성
    const mask = new Uint8ClampedArray(imgAData.data.length);
    for (let i = 0; i < imgAData.data.length; i += 4) {
      const diff = Math.abs(imgAData.data[i] - imgBData.data[i]);
      mask[i] = diff > 50 ? 255 : 0; // Threshold
    }

    return mask;
  };

  const applyAdjustments = (
    ctx: CanvasRenderingContext2D,
    img: HTMLImageElement,
    mask: Uint8ClampedArray,
    brightness: number,
    colorTemp: number
  ) => {
    ctx.drawImage(img, 0, 0);
    const imgData = ctx.getImageData(0, 0, img.width, img.height);
    const data = imgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const maskValue = mask[i] / 255; // Normalized mask value

      // 밝기 조정
      data[i] = data[i] * (1 + maskValue * (brightness - 1)); // Red
      data[i + 1] = data[i + 1] * (1 + maskValue * (brightness - 1)); // Green
      data[i + 2] = data[i + 2] * (1 + maskValue * (brightness - 1)); // Blue

      // 색온도 조정
      data[i] += maskValue * colorTemp; // Red channel
      data[i + 2] -= maskValue * colorTemp; // Blue channel
    }

    ctx.putImageData(imgData, 0, 0);
  };

  const handleBrightnessChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBrightness(parseFloat(e.target.value));
  };

  const handleColorTempChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setColorTemp(parseInt(e.target.value, 10));
  };

  return (
    <div className="bg-black min-h-screen flex flex-col items-center justify-center text-white">
      <h1 className="text-2xl font-bold mb-6">Apply Brightness and Color Temperature</h1>

      {/* 캔버스 */}
      <div className="bg-white p-5 rounded-lg shadow-md">
        <canvas ref={canvasRef} className="rounded-md" />
      </div>

      {/* 슬라이더 */}
      <div className="mt-10 bg-gray-800 p-5 rounded-lg w-3/4 lg:w-1/2">
        <div className="mb-5">
          <label htmlFor="brightness" className="block text-lg font-semibold mb-2">
            Brightness: {brightness.toFixed(1)}
          </label>
          <input
            id="brightness"
            type="range"
            min="1.0"
            max="2.0"
            step="0.1"
            value={brightness}
            onChange={handleBrightnessChange}
            className="w-full"
          />
        </div>
        <div>
          <label htmlFor="colorTemp" className="block text-lg font-semibold mb-2">
            Color Temperature: {colorTemp}
          </label>
          <input
            id="colorTemp"
            type="range"
            min="-50"
            max="50"
            step="1"
            value={colorTemp}
            onChange={handleColorTempChange}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );
};

export default ApplyBrightPage;
