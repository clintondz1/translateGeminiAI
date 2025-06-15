# 🤖 translateAI Bot

Bot Telegram thông minh hỗ trợ dịch thuật đa ngôn ngữ với công nghệ AI tiên tiến.

## ✨ Tính năng

- 🔄 **Dịch thuật đa ngôn ngữ**: Hỗ trợ hơn 100 ngôn ngữ
- 🎯 **Nhận diện ngôn ngữ tự động**: Tự động phát hiện ngôn ngữ nguồn
- 📱 **Giao diện thân thiện**: Commands đơn giản, dễ sử dụng
- ⚡ **Tốc độ nhanh**: Phản hồi trong vài giây
- 🔒 **Bảo mật cao**: Không lưu trữ dữ liệu người dùng
- 🎨 **Tối ưu hóa**: Code clean, hiệu suất cao

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Node.js >= 16.0.0 (hoặc Python >= 3.8)
- npm hoặc yarn
- Telegram Bot Token

### Cài đặt dependencies
```bash
git clone https://github.com/dintond21/translateAI.git
cd translateAI
npm install
```

### Cấu hình
1. Tạo file `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
NODE_ENV=production
```

2. Cập nhật cấu hình trong `config/settings.js`

## 🔧 Sử dụng

### Khởi chạy bot
```bash
# Development mode
npm run dev

# Production mode
npm start
```

### Commands bot
- `/start` - Khởi động bot
- `/help` - Hướng dẫn sử dụng
- `/translate <text>` - Dịch văn bản
- `/lang <code>` - Đặt ngôn ngữ đích
- `/detect <text>` - Nhận diện ngôn ngữ

### Ví dụ sử dụng
```
User: /translate Hello world
Bot: Xin chào thế giới

User: /lang ja
Bot: ✅ Đã đặt ngôn ngữ đích: Tiếng Nhật

User: /translate Good morning
Bot: おはようございます
```

## 🧪 Testing

```bash
# Chạy tất cả tests
npm test

# Test với coverage
npm run test:coverage

# Test integration
npm run test:integration
```

## 📁 Cấu trúc dự án

```
translateAI/
├── src/
│   ├── bot/           # Bot logic
│   ├── services/      # Translation services
│   ├── utils/         # Utilities
│   ├── config/        # Configuration
│   └── middleware/    # Middleware
├── tests/             # Test files
├── docs/              # Documentation
├── .github/           # GitHub workflows
├── logs/              # Log files
└── README.md
```

## 🔄 Workflow phát triển

1. **Fork** repository này
2. Tạo **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** thay đổi: `git commit -m 'Add amazing feature'`
4. **Push** lên branch: `git push origin feature/amazing-feature`
5. Tạo **Pull Request**

## 📝 Changelog

### v1.0.0 (2025-06-16)
- ✨ Phiên bản đầu tiên với code tối ưu
- 🔄 Dịch thuật đa ngôn ngữ
- 🤖 Tích hợp AI translation
- 📱 Giao diện Telegram bot
- 🧪 Unit tests và CI/CD

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết chi tiết.

## 📄 License

Dự án này sử dụng [MIT License](LICENSE).

## 👨‍💻 Tác giả

**dintond21**
- GitHub: [@dintond21](https://github.com/dintond21)
- Email: your.email@example.com

## 🙏 Acknowledgments

- OpenAI API cho dịch thuật AI
- Telegram Bot API
- Cộng đồng open source

---
⭐ **Nếu project hữu ích, hãy cho một star nhé!** ⭐
