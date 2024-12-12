"use client";
import { useState, useEffect } from 'react';
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";

const LocationPage = () => {
    const router = useRouter();
    const [images, setImages] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchImageData = async () => {
            try {
                const response = await fetch('/api/location-coordinates');
                if (!response.ok) {
                    throw new Error('Failed to fetch image data');
                }
                const data = await response.json();
                setImages(data.images);
                setIsLoading(false);
            } catch (err) {
                console.error(err);
                setError(err instanceof Error ? err.message : 'An unknown error occurred');
                setIsLoading(false);
            }
        };

        fetchImageData();
    }, []);

    const handleIconClick = (clusterId: number) => {
        router.push(`/selectloc?clusterId=${clusterId}`);
    };

    if (isLoading) {
        return <div>로딩 중...</div>;
    }

    if (error) {
        return <div>오류: {error}</div>;
    }

    return (
        <div className="bg-black flex flex-col min-h-screen">
            <div className="flex justify-center">
                <Navbar backgroundColor="rgb(0, 0, 0)" />
            </div>

            <div className="flex flex-grow justify-center items-center mt-10">
                <div className="bg-white rounded-lg shadow-md p-6 text-center w-[320px] relative">
                    {images.map((imageData, index) => (
                        <div key={index} className="relative w-full h-[300px] mb-4">
                            <img
                                src={imageData.s3_url || "/placeholder.jpg"}
                                alt={`Uploaded ${imageData.image_name}`}
                                className="w-full h-full object-cover rounded-md"
                            />
                            {imageData.mask_images && imageData.mask_images.map((maskImage: any) => (
                                <img
                                    key={maskImage.cluster_id}
                                    src="/images/loc.png"
                                    alt={`Location Icon ${maskImage.cluster_id}`}
                                    className="absolute cursor-pointer"
                                    style={{
                                        top: `${maskImage.cluster_center.y}px`,
                                        left: `${maskImage.cluster_center.x}px`,
                                        width: "35px",
                                        height: "35px",
                                    }}
                                    onClick={() => handleIconClick(maskImage.cluster_id)}
                                />
                            ))}
                        </div>
                    ))}
                    <div className="flex items-center justify-center mt-5 space-x-2">
                        <p className="text-gray-800 font-custom">위치를 선택하세요</p>
                        <img
                            src="/images/loc.png"
                            alt="Location Icon"
                            className="w-5 h-5"
                        />
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
};

export default LocationPage;