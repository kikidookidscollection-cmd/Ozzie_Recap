import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import requests
import io
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup

st.set_page_config(page_title="Ultimate Clip AI", page_icon="🎬", layout="wide")

st.title("🎬 Ultimate AI Shorts Generator")
st.markdown("YouTube Link၊ Website Link (သို့) ရုပ်ရှင်အမည် ထည့်သွင်းရုံဖြင့် TikTok/Shorts အတွက် ဗိုင်းရပ်ဖြစ်နိုင်မယ့် ဇာတ်ညွှန်းတို (၃) ခုကို အလိုအလျောက် ထုတ်ပေးပါမည်။")

with st.sidebar:
    st.header("⚙️ API Keys")
    api_key = st.text_input("Gemini API Key", type="password")
    tmdb_api_key = st.text_input("TMDB API Key (ရွေးချယ်ရန်)", type="password")
    
user_input = st.text_input("🔍 YouTube Link, Website Link သို့မဟုတ် ရုပ်ရှင်အမည် ရိုက်ထည့်ပါ", placeholder="ဥပမာ - https://youtu.be/... သို့မဟုတ် The Matrix")
generate_btn = st.button("Viral Clips ၃ ခု ဖန်တီးပါ 🚀", use_container_width=True)

# --- Functions ---
def extract_video_id(url):
    try:
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0][:11]
        elif "watch?v=" in url:
            return url.split("watch?v=")[1].split("&")[0][:11]
    except:
        return None
    return None

def scrape_website_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:10000]
    except Exception as e:
        return None

# --- Main Logic ---
if generate_btn and api_key and user_input:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        video_context = ""
        
        # ၁။ Input သည် YouTube Link ဖြစ်နေလျှင်
        if "youtube.com" in user_input or "youtu.be" in user_input:
            video_id = extract_video_id(user_input)
            if video_id:
                with st.spinner("📥 YouTube မှ စကားပြောများ ဆွဲယူနေပါသည်..."):
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                        video_context = " ".join([t['text'] for t in transcript_list])
                        st.success("YouTube မှ အချက်အလက်များ အောင်မြင်စွာ ရယူနိုင်ပါပြီ။")
                    except Exception:
                        st.warning("ဤ ဗီဒီယိုတွင် Subtitle (Transcript) မပါဝင်ပါ။ AI မှ ခေါင်းစဉ်ကိုသာ ကြည့်၍ ဖန်တီးပေးပါမည်။")
                        video_context = f"Video Link: {user_input}"
            else:
                st.warning("⚠️ YouTube Link ပုံစံ မှားယွင်းနေပါသည်။")
                        
        # ၂။ Input သည် အခြား Website Link ဖြစ်နေလျှင်
        elif user_input.startswith("http://") or user_input.startswith("https://"):
            with st.spinner("🌐 Website မှ အချက်အလက်များ ဆွဲယူနေပါသည်..."):
                scraped_text = scrape_website_text(user_input)
                if scraped_text and len(scraped_text.strip()) > 50:
                    video_context = f"အောက်ပါ Website မှ ရရှိသော အချက်အလက်များ: {scraped_text}"
                    st.success("Website မှ အချက်အလက်များ အောင်မြင်စွာ ရယူနိုင်ပါပြီ။")
                else:
                    st.warning("Website မှ စာသားများကို ဆွဲယူ၍ မရပါ။")
                    video_context = f"Link: {user_input}"
                    
        # ၃။ Input သည် ရုပ်ရှင်နာမည် ဖြစ်နေလျှင်
        else:
            video_context = f"ရုပ်ရှင်အမည် - {user_input}"
            if tmdb_api_key:
                search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={user_input}"
                response = requests.get(search_url).json()
                if response.get('results') and response['results'][0].get('poster_path'):
                    poster_url = f"https://image.tmdb.org/t/p/w500{response['results'][0]['poster_path']}"
                    st.image(poster_url, width=300)

        # AI သို့ စေခိုင်းခြင်း
        if video_context:
            prompt = f"""
            အောက်ပါ အချက်အလက်များအပေါ် အခြေခံ၍ TikTok/Shorts တွင် တင်ရန် အလွန်ဆွဲဆောင်မှုရှိသော (၁ မိနစ်စာ) ဇာတ်ညွှန်းတို (၃) ခုကို မြန်မာဘာသာဖြင့် ရေးပေးပါ။
            အချက်အလက်: {video_context}
            
            ဇာတ်ညွှန်းတစ်ခုစီကို အောက်ပါပုံစံအတိုင်း တိတိကျကျ ရေးပါ-
            
            ခေါင်းစဉ်: [ဆွဲဆောင်မှုရှိသော Clickbait ခေါင်းစဉ်]
            Virality Score: [လူကြည့်များနိုင်ချေ 1 မှ 100 အတွင်း အမှတ်ပေးရန်]
            ဇာတ်ညွှန်း: [ပြောရမည့် စာသားများ]
            ---
            """
            
            with st.spinner("⏳ ဇာတ်ညွှန်း (၃) ခုကို ခွဲခြမ်းစိတ်ဖြာနေပါသည်..."):
                response = model.generate_content(prompt)
                clips = response.text.split('---') 
            
            # ဇာတ်ညွှန်း တစ်ခုစီကို ခွဲ၍ ပြသခြင်းနှင့် အသံထုတ်ခြင်း
            for index, clip in enumerate(clips):
                if clip.strip() and "ခေါင်းစဉ်:" in clip:
                    with st.container():
                        st.markdown(f"### 🎬 Clip {index + 1}")
                        st.markdown(clip)
                        
                        with st.spinner("🎧 အသံဖိုင် ဖန်တီးနေပါသည်..."):
                            tts = gTTS(text=clip.strip(), lang='my', slow=False)
                            sound_file = io.BytesIO()
                            tts.write_to_fp(sound_file)
                            st.audio(sound_file, format='audio/mp3')
                        st.markdown("---")
            
    except Exception as e:
        st.error(f"❌ အမှားအယွင်း ဖြစ်ပေါ်နေပါသည်: {e}")
