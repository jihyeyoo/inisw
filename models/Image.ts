import mongoose from 'mongoose';

const ImageSchema = new mongoose.Schema({
    image_name: {
        type: String,
        required: true
    },
    s3_url: {
        type: String,
        required: true,
        unique: true
    },
    uploaded_at: {
        type: Date,
        default: Date.now
    }
}, {
    collection: 'images', // 컬렉션 이름 설정
});

export default mongoose.models.Image || mongoose.model('Image', ImageSchema);