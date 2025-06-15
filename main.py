# Deploy Telegram Translation Bot trên Railway

## Bước 1: Chuẩn bị code cho Railway

### 1.1 Tạo file main.py (đã được tối ưu)
```python
import asyncio
import aiohttp
import re
import json
import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramTranslateBot:
    def __init__(self, telegram_token, gemini_api_key):
        self.telegram_token = telegram_token
        self.gemini_api_key = gemini_api_key
        self.session = None
        self.translation_cache = {}
        self.user_settings = {}
        self.extended_dict = self.load_extended_dictionary()

    def load_extended_dictionary(self):
        """Từ điển mở rộng cho dịch nhanh các từ thông dụng"""
        return {
            '你好': 'Xin chào', '再见': 'Tạm biệt', '谢谢': 'Cảm ơn', '对不起': 'Xin lỗi',
            '我': 'Tôi', '你': 'Bạn', '他': 'Anh ấy', '她': 'Cô ấy', '我们': 'Chúng tôi',
            '是': 'là', '不是': 'không phải', '有': 'có', '没有': 'không có',
            '好': 'tốt', '不好': 'không tốt', '可以': 'có thể', '不可以': 'không thể',
            'Xin chào': '你好', 'Cảm ơn': '谢谢', 'Tôi': '我', 'Bạn': '你',
            'Chúng tôi': '我们', 'là': '是', 'không': '不', 'có': '有'
        }

    async def get_session(self):
        """Tạo session HTTP nếu chưa có"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    def contains_chinese(self, text):
        """Kiểm tra có tiếng Trung không"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def contains_vietnamese(self, text):
        """Kiểm tra có tiếng Việt không (dấu thanh)"""
        return bool(re.search(r'[ăâđêôơưĂÂĐÊÔƠƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]', text))

    def detect_language(self, text):
        """Tự động phát hiện ngôn ngữ"""
        if self.contains_chinese(text):
            return 'zh'
        elif self.contains_vietnamese(text):
            return 'vi'
        else:
            return 'en'

    async def translate_with_gemini(self, text, target_lang='vi'):
        """Dịch văn bản bằng Gemini Flash API"""
        cache_key = (text, target_lang)
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        session = await self.get_session()

        lang_names = {
            'vi': 'tiếng Việt',
            'zh': 'tiếng Trung (Simplified Chinese)',
            'en': 'tiếng Anh'
        }

        target_lang_name = lang_names.get(target_lang, 'tiếng Việt')

        prompt = f"""Hãy dịch văn bản sau sang {target_lang_name} một cách tự nhiên và chính xác nhất:

"{text}"

Chỉ trả về bản dịch, không thêm giải thích hay ghi chú gì khác."""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"

            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1000,
                }
            }

            headers = {
                "Content-Type": "application/json"
            }

            async with session.post(url, json=payload, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'candidates' in data and len(data['candidates']) > 0:
                        translation = data['candidates'][0]['content']['parts'][0]['text'].strip()
                        self.translation_cache[cache_key] = translation
                        return translation
                else:
                    logger.error(f"Gemini API error: {response.status}")

        except Exception as e:
            logger.error(f"Error translating with Gemini: {e}")

        return None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /start"""
        user_id = update.effective_user.id
        self.user_settings[user_id] = {
            'auto_translate': False,
            'preferred_target': 'vi'
        }

        keyboard = [
            [InlineKeyboardButton("🔧 Cài đặt", callback_data="settings")],
            [InlineKeyboardButton("📖 Hướng dẫn", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = """🤖 **Bot Dịch Đa Ngôn Ngữ**

🌟 Tôi có thể dịch:
• Tiếng Trung → Tiếng Việt
• Tiếng Việt → Tiếng Trung  
• Bất kỳ ngôn ngữ nào → Tiếng Việt

🚀 **Cách sử dụng:**
• `/dich <văn bản>` - Tự động phát hiện và dịch
• `/dich_zh <văn bản>` - Dịch sang tiếng Trung
• `/dich_vi <văn bản>` - Dịch sang tiếng Việt
• `/auto_on` - Bật dịch tự động
• `/auto_off` - Tắt dịch tự động

Powered by Google Gemini Flash ⚡"""

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /help"""
        help_text = """📖 **Hướng Dẫn Sử Dụng**

**Lệnh dịch:**
• `/dich <text>` - Tự động nhận diện và dịch
• `/dich_zh <text>` - Dịch sang tiếng Trung
• `/dich_vi <text>` - Dịch sang tiếng Việt

**Chế độ tự động:**
• `/auto_on` - Bật dịch tự động mọi tin nhắn
• `/auto_off` - Tắt dịch tự động

**Thống kê:**
• `/stats` - Xem thống kê bot

**Ví dụ:**
```
/dich 你好世界
/dich Xin chào thế giới
/dich_zh Hello world
```

🔥 **Tính năng đặc biệt:**
• Sử dụng AI Gemini Flash cho độ chính xác cao
• Cache thông minh giảm thời gian phản hồi
• Hỗ trợ dịch đa ngôn ngữ sang tiếng Việt"""

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /stats"""
        stats_text = f"""📊 **Thống Kê Bot**

🔤 Từ điển: {len(self.extended_dict)} từ/cụm từ
💾 Cache dịch: {len(self.translation_cache)} bản dịch
👥 Người dùng: {len(self.user_settings)} users
🤖 Engine: Google Gemini Flash
🚀 Hosted on Railway

⏰ Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

        await update.message.reply_text(stats_text, parse_mode='Markdown')

    async def auto_on_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bật dịch tự động"""
        user_id = update.effective_user.id
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id]['auto_translate'] = True

        await update.message.reply_text(
            "✅ Đã bật dịch tự động! Tôi sẽ dịch mọi tin nhắn có tiếng Trung hoặc tiếng Việt.")

    async def auto_off_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tắt dịch tự động"""
        user_id = update.effective_user.id
        if user_id not in self.user_settings:
            self.user_settings[user_id] = {}
        self.user_settings[user_id]['auto_translate'] = False

        await update.message.reply_text("❌ Đã tắt dịch tự động! Sử dụng lệnh /dich để dịch thủ công.")

    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /dich - tự động phát hiện ngôn ngữ"""
        if not context.args:
            await update.message.reply_text("❌ Vui lòng nhập văn bản cần dịch!\nVí dụ: `/dich 你好世界`",
                                            parse_mode='Markdown')
            return

        text = ' '.join(context.args)
        src_lang = self.detect_language(text)

        if src_lang == 'zh':
            target_lang = 'vi'
        elif src_lang == 'vi':
            target_lang = 'zh'
        else:
            target_lang = 'vi'

        await self.perform_translation(update, text, src_lang, target_lang, manual=True)

    async def translate_to_chinese_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /dich_zh - dịch sang tiếng Trung"""
        if not context.args:
            await update.message.reply_text("❌ Vui lòng nhập văn bản cần dịch!\nVí dụ: `/dich_zh Xin chào`",
                                            parse_mode='Markdown')
            return

        text = ' '.join(context.args)
        await self.perform_translation(update, text, self.detect_language(text), 'zh', manual=True)

    async def translate_to_vietnamese_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lệnh /dich_vi - dịch sang tiếng Việt"""
        if not context.args:
            await update.message.reply_text("❌ Vui lòng nhập văn bản cần dịch!\nVí dụ: `/dich_vi Hello world`",
                                            parse_mode='Markdown')
            return

        text = ' '.join(context.args)
        await self.perform_translation(update, text, self.detect_language(text), 'vi', manual=True)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý tin nhắn thường (dịch tự động nếu được bật)"""
        user_id = update.effective_user.id

        if user_id not in self.user_settings or not self.user_settings[user_id].get('auto_translate', False):
            return

        text = update.message.text
        src_lang = self.detect_language(text)

        if src_lang in ['zh', 'vi']:
            target_lang = 'vi' if src_lang == 'zh' else 'zh'
            await self.perform_translation(update, text, src_lang, target_lang, manual=False)

    async def perform_translation(self, update: Update, text: str, src_lang: str, target_lang: str,
                                  manual: bool = False):
        """Thực hiện dịch và gửi kết quả"""
        processing_msg = await update.message.reply_text("🔄 Đang dịch...")

        try:
            translation = await self.translate_with_gemini(text, target_lang)

            if translation:
                lang_flags = {'zh': '🇨🇳', 'vi': '🇻🇳', 'en': '🇺🇸'}
                src_flag = lang_flags.get(src_lang, '🌐')
                target_flag = lang_flags.get(target_lang, '🌐')

                mode_text = "🎯 Thủ công" if manual else "🤖 Tự động"

                result_text = f"""**{src_flag} → {target_flag} Dịch thuật** {mode_text}

📝 **Gốc:**
{text}

✨ **Dịch:**
{translation}

⚡ _Powered by Gemini Flash_
🕐 {datetime.now().strftime('%H:%M:%S')}"""

                await processing_msg.edit_text(result_text, parse_mode='Markdown')
            else:
                await processing_msg.edit_text("❌ Không thể dịch văn bản này. Vui lòng thử lại!")

        except Exception as e:
            logger.error(f"Translation error: {e}")
            await processing_msg.edit_text("❌ Có lỗi xảy ra khi dịch. Vui lòng thử lại!")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý callback từ inline buttons"""
        query = update.callback_query
        await query.answer()

        if query.data == "help":
            await self.help_command(query, context)
        elif query.data == "settings":
            user_id = query.from_user.id
            auto_status = "Bật" if self.user_settings.get(user_id, {}).get('auto_translate', False) else "Tắt"

            keyboard = [
                [InlineKeyboardButton("🔄 Toggle Auto Translate", callback_data="toggle_auto")],
                [InlineKeyboardButton("🏠 Về trang chủ", callback_data="home")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            settings_text = f"""⚙️ **Cài Đặt**

🤖 Dịch tự động: **{auto_status}**
🌐 Ngôn ngữ ưu tiên: Tiếng Việt

Chọn tùy chọn bên dưới:"""

            await query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')

        elif query.data == "toggle_auto":
            user_id = query.from_user.id
            if user_id not in self.user_settings:
                self.user_settings[user_id] = {}

            current_status = self.user_settings[user_id].get('auto_translate', False)
            self.user_settings[user_id]['auto_translate'] = not current_status

            new_status = "Bật" if not current_status else "Tắt"
            await query.edit_message_text(f"✅ Đã {new_status.lower()} chế độ dịch tự động!")

    async def close(self):
        """Đóng session"""
        if self.session:
            await self.session.close()

    def run(self):
        """Chạy bot"""
        application = Application.builder().token(self.telegram_token).build()

        # Thêm handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("auto_on", self.auto_on_command))
        application.add_handler(CommandHandler("auto_off", self.auto_off_command))
        application.add_handler(CommandHandler("dich", self.translate_command))
        application.add_handler(CommandHandler("dich_zh", self.translate_to_chinese_command))
        application.add_handler(CommandHandler("dich_vi", self.translate_to_vietnamese_command))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Chạy bot
        logger.info("🤖 Bot Telegram Translation đã bắt đầu trên Railway!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Lấy token từ environment variables (bảo mật hơn)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Kiểm tra token
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        logger.error("❌ Vui lòng cài đặt TELEGRAM_TOKEN và GEMINI_API_KEY trong Environment Variables!")
        exit(1)

    try:
        bot = TelegramTranslateBot(TELEGRAM_TOKEN, GEMINI_API_KEY)
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot đã dừng")
    except Exception as e:
        logger.error(f"❌ Lỗi: {e}")
        logger.error("1. Kiểm tra TELEGRAM_TOKEN")
        logger.error("2. Kiểm tra GEMINI_API_KEY")
        logger.error("3. Kiểm tra kết nối mạng")