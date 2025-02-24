// /app/location/page.tsx
"use client";
import { useState, useEffect } from 'react';
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import { useRouter } from "next/navigation";

const LocationPage = () => {
    const router = useRouter();
    const [images, setImages] = useState<any[]>([]);
    const [latestImage, setLatestImage] = useState<any | null>(null);
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

                const latestImageResponse = await fetch('/api/latest-image');
                if (!latestImageResponse.ok) {
                    throw new Error('Failed to fetch latest image');
                }
                const latestImageData = await latestImageResponse.json();
                setLatestImage(latestImageData.image);
                setIsLoading(false);
            } catch (err) {
                console.error(err);
                setError(err instanceof Error ? err.message : 'Unknown error occurred');
                setIsLoading(false);
            }
        };

        fetchImageData();
    }, []);

    const processDiffusionImage = async (
        imageUrl: string,
        maskUrl: string,
        referenceUrl: string,
        outputDir: string
    ) => {
        const response = await fetch('http://localhost:8080/process_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_path: imageUrl,
                mask_path: maskUrl,
                reference_path: referenceUrl,
                output_dir: outputDir,
                seed: 321,
                scale: 20,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to process image with ${referenceUrl}`);
        }

        return await response.json();
    };

    const handleIconClick = async (clusterId: number) => {
        setIsLoading(true);
        try {
            if (!latestImage) {
                throw new Error('No latest image data available');
            }

            const bucketName = process.env.NEXT_PUBLIC_AWS_S3_BUCKET_NAME;
            const region = process.env.NEXT_PUBLIC_AWS_S3_REGION;

            if (!bucketName || !region) {
                throw new Error('Missing AWS environment variables');
            }

            const maskImageUrl = `https://${bucketName}.s3.${region}.amazonaws.com/${latestImage.image_name}-masks/mask_cluster_${clusterId}.png`;

            // Process images with different lamps in parallel
            const lampUrls = [
                "https://lumterior.s3.ap-northeast-2.amazonaws.com/lamp/lamp1.png",
                // "https://lumterior.s3.ap-northeast-2.amazonaws.com/lamp/lamp2.png",
                // "https://lumterior.s3.ap-northeast-2.amazonaws.com/lamp/lamp3.png"
            ];

            // URL 확인
            lampUrls.forEach((lampUrl, index) => {
                console.log(`Lamp URL ${index + 1}:`, lampUrl);
            });

            const processPromises = lampUrls.map((lampUrl, index) =>
                processDiffusionImage(
                    latestImage.s3_url,
                    maskImageUrl,
                    lampUrl,
                    `lamp${index + 1}_results`
                )
            );

            const results = await Promise.all(processPromises);
            console.log('Response from processDiffusionImage:', results); // 응답 내용 출력

            // Generate masks for each processed image
            const maskPromises = results.map((result, index) =>
                fetch('http://localhost:8080/generate_mask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        processed_image_path: result.processed_image_path,
                        original_image_path: latestImage.s3_url,
                        reference_path: lampUrls[index]
                    }),
                })
            );

            await Promise.all(maskPromises);

            // Store results in local storage or context for the next page
            localStorage.setItem('processedImages', JSON.stringify(results));
            router.push(`/selectloc?clusterId=${clusterId}`);

        } catch (err) {
            console.error('Diffusion model execution error:', err);
            console.error('Error details:', err instanceof Error ? err.stack : 'No stack available');
            setError(err instanceof Error ? err.message : 'Unknown error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return <div className="flex justify-center items-center min-h-screen">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
        </div>;
    }

    if (error) {
        return <div className="flex justify-center items-center min-h-screen text-red-600">
            Error: {error}
        </div>;
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
                                    alt={`cluster_id ${maskImage.cluster_id}`}
                                    className="absolute cursor-pointer hover:scale-110 transition-transform"
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