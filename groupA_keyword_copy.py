import streamlit as st
import numpy as np
from pandas import DataFrame
from keybert import KeyBERT
import seaborn as sns
import os, glob, pathlib, random, pickle, time, requests, json, commons
import io
from io import StringIO, BytesIO
from pathlib import Path
from collections import Counter
import uuid
from itertools import chain
from sftp import SFTP
from PIL import Image
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

hide_menu = """
<style>
#MainMenu {
    visibility:hidden;
}
</style>
"""


st.set_page_config(initial_sidebar_state="collapsed")

# set session_state for change pages
st.session_state.update(st.session_state)
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Home'
    

def save_keyword_tag_result(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords):
    # conv_change = []
    # for i, c in enumerate(change):
    #     target = c
    #     if c == "-":
    #         target = selected_tags[i]
    #     conv_change.append(target)
    # print(conv_change)
    results_B = {'Scenario':scenario, 'Text': doc, 'Keywords': keywords, 'Added keywords': added_keywords, 'Final aggregated keywords': final_aggregated_keywords}
    if not os.path.exists(save_path):
        data = {}
        data['submits'] = []
        data['submits'].append(results_B)
        print("no exists", data)
        with open(save_path, 'w') as save_f:
            json.dump(data, save_f, ensure_ascii=False, indent=4)

    else:
        data = {}
        with open(save_path, "r") as json_file:
            data = json.load(json_file)
        data['submits'].append(results_B)
        print("exists, before", data)

        with open(save_path, "w") as save_f:
            json.dump(data, save_f, ensure_ascii=False, indent=4)
            print("exists, after", data)

# callback functions for change page
def CB_Home():
    st.session_state.active_page = 'Page_1'

# def CB_Page0():
#     st.session_state.active_page = 'Page_1'

def CB_Page1(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords):
    save_keyword_tag_result(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords)
    music_retrieval()
    st.session_state.active_page = 'Page_2'

def CB_Page2():
    st.session_state.active_page = 'Page_3'

def CB_Page3(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords):
    save_keyword_tag_result(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords)
    music_retrieval()
    st.session_state.active_page = 'Page_4'

def CB_Page4():
    st.session_state.active_page = 'Page_5'

def CB_Page5(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords):
    save_keyword_tag_result(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords)
    music_retrieval()
    st.session_state.active_page = 'Page_6'

def CB_Page6():
    st.session_state.active_page = 'Page_9'

# def CB_Page7(save_path, clicked, selected_tags, satis_result, change):
#     save_image_tag_result(save_path, clicked, selected_tags, satis_result, change)
#     music_retrieval()
#     st.session_state.active_page = 'Page_8'

# def CB_Page8():
#     st.session_state.active_page = 'Page_9'

def CB_Page9():
    st.session_state.active_page = 'Page_10'


sftp = SFTP(st.secrets["HOSTNAME"], st.secrets["USERNAME"], st.secrets["PASSWORD"])

def home():
    id = str(uuid.uuid4())
    st.session_state['id'] = id
    result_file_name = id + ".json"
    save_path = get_result_dir() + "/" + result_file_name
    
    header = st.container()
    with header:
        title = st.title("Let's find music! 🎵")
        st.markdown(hide_menu, unsafe_allow_html = True)

        sh1 = st.container()
        with sh1:
            subheader2 = st.subheader('🧪 In this experiment:')
            st.markdown("In this experiment, participants will try out the music search system.") 
            st.markdown("Our system searches for music that fits your mood or specific situation.")
            st.markdown("- STEP 1: We provide three scenarios.")
            st.markdown("- STEP 2: Please select your preferred scenario from the three provided options, and enter a short descriptive text that suits the chosen scenario to search for music.")
            st.markdown("- STEP 3: Our system extracts keywords from the text you provided.")
            st.markdown("- STEP 4: You can add keywords to make your search more accurate.")
            st.markdown("- STEP 5: Now, please enjoy the searched music.")
            st.markdown("- STEP 6: Repeat the process two more times.")
            #STEP 1: 세 가지 시나리오를 제공해 드립니다.
            # STEP 2: 제공된 세 가지 시나리오 중 원하는 시나리오를 선택하고 해당 시나리오에 어울리는 짧은 텍스트를 입력하여 음악을 검색하세요.
            #STEP 3: 검색된 음악을 감상해주세요.
            #STEP 4: 두 번 더 해당 프로세스를 반복합니다. 
        st.write('-----')

        sh2 = st.container()
        with sh2:
            subheader3 = st.subheader('👀 Caution')
            st.markdown("- **Please read the description carefully and follow the instructions. If you skip steps, your participation in the experiment may not be complete.**")
            # st.caption("- 시스템이 작동되지 않거나, 오류 메시지가 표시될 경우 손을 들어 연구자에게 알려주세요.")
            st.markdown("- **The searched music is copyright-free music provided for research purposes.**")
            st.markdown("- Therefore, please note that <span style='color:red'> the searched music may be different from the latest music you are familiar with.</span>",unsafe_allow_html=True)
            st.write('-----')

        st.experimental_set_query_params(path=save_path)
        st.button('Agree, Start', on_click=CB_Home)
 

 ## ------------------ Instruction warning ----------------------------
# def note():
#     st.markdown(hide_menu, unsafe_allow_html = True)
#     image = Image.open('note.png')
#     st.image(image, caption='Caution', width = 1000)

#     st.button('Confirmed', on_click=CB_Page0)
 ## ------------------ for Keyword Retrieval ------------------------ 
def get_result_dir():
    path = os.getcwd() + "/results"
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
    print("created result dir: " + path)
    return path

def _max_width_():
    max_width_str = f"max-width: 1400px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


_max_width_()

music_tags = [
    '-', 'action', 'adventure', 'advertising', 'background', 'ballad', 'calm', 'children', 'christmas', 'commercial', 'cool', 'corporate',
    'dark', 'deep', 'documentary', 'drama', 'dramatic', 'dream', 'emotional', 'energetic', 'epic', 'fast', 'film', 'fun', 'funny', 'game',
    'groovy', 'happy', 'heavy', 'holiday', 'hopeful', 'inspiring', 'love', 'meditative', 'melancholic', 'melodic', 'motivational',
    'movie', 'nature', 'party', 'positive', 'powerful', 'relaxing', 'retro', 'romantic', 'sad', 'sexy', 'slow', 'soft', 'soundscape', 
    'space', 'sport', 'summer', 'trailer', 'travel', 'upbeat', 'uplifting'
    ]


def text_page1(cb):
    # show frontend title 
    st.title("Let's find music!")
    st.markdown('✔️ STEP 1: Please select your preferred scenario from the three provided options.')
    scenario = st.radio(
    "Please select a scenario that you preferred the most.",
    ('Feeling tired but unable to sleep.', 
    'During exercise (yoga or fitness, etc.).', 
    'Preparing for a party.'))
    if scenario == 'Feeling tired but unable to sleep.':
        st.markdown("<span style='color:blue'>Example: a quiet, peaceful song good for sleeping.</span>",unsafe_allow_html=True)
    elif scenario == 'During exercise (yoga or fitness, etc.).':
        st.markdown("<span style='color:blue'>Example: meditative songs that are good to listen to while doing yoga.</span>",unsafe_allow_html=True)
    else: 
        st.markdown("<span style='color:blue'>Example: upbeat and trendy song.</span>",unsafe_allow_html=True)
    # st.markdown("✔️ Please describe the mood of the music you want to hear or the situation where you need music. We recommend music based on the entered text.")
    st.markdown("✔️ STEP 2: Enter a short descriptive text that suits the chosen scenario to search for music. We will find music that matches the text you have typed.")
    st.markdown("✔️ STEP 3: After entering the text, click the button below and wait for a while until the next process.")
    st.error("⚠️The system may take a little time to initialize for the first run. From the second time onwards, it will be instant, so don't worry!")
    st.markdown(hide_menu, unsafe_allow_html = True)
    st.write("---")
    save_path = st.experimental_get_query_params()['path'][0]
    # with st.container():
    #     st.markdown("<span style='color:blue'>Choose one of the three provided scenarios that you prefer, and enter a descriptive text about that scenario to search for music.</span>",unsafe_allow_html=True)
    
    # # st.subheader("Choose one of the three provided scenarios that you prefer, and enter a descriptive text about that scenario to search for music.")
    # def scenario_selector (scenario):
    #     for i in scenario:
    #         st.markdown(i)



    # # 함수 콜백
    # if st.session_state.active_page == 'Page_1':
    #     length = scenario_selector(scenario1)
    # elif st.session_state.active_page == 'Page_3':
    #     length = scenario_selector(scenario2)
    # elif st.session_state.active_page == 'Page_5':
    #     length = scenario_selector(scenario3)
    # show imgs to be selected    

    
    selection = st.container()
    with selection:
        try:
            c1, c2, c3 = st.columns([0.07, 5, 0.07])
            with c1:
                @st.cache_resource
                # @st.cache(allow_output_mutation=True)
                def load_model():
                    return KeyBERT()

                kw_model = load_model()

            with c2:
                doc = st.text_area(
                    "Type the text below (max 500 words)",
                    height=100,
                )

                MAX_WORDS = 500
                import re
                res = len(re.findall(r"\w+", doc))
                if res > MAX_WORDS:
                    st.warning(
                        "⚠️ Your text contains "
                        + str(res)
                        + " words."
                        + " Only the first 500 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
                    )

                    doc = doc[:MAX_WORDS]
                    
                # submit_button = st.form_submit_button(label="✨ Get me the data!")
                submit_button = st.button('✨ Get me the keywords!')

            global stopwords
            stopwords = stopwords.words('english')
            stop_list = ["song", "songs", "music", "search", "retrieve", "listen", "hear"]
            stpwrd = nltk.corpus.stopwords.words('english')
            stpwrd.extend(stop_list)
            
            if not submit_button and 'keep_going' not in st.session_state:
                st.session_state.keep_going = False
            else:
                st.session_state.keep_going = True
            
            if st.session_state.keep_going == False:
                st.stop()

            keywords = kw_model.extract_keywords(
                doc,
                keyphrase_ngram_range=(1, 1),
                use_mmr=False,
                stop_words=stpwrd, #StopWords
                top_n=5,
                # diversity=Diversity,
            )

            if len(keywords)==0:
                st.warning(
                        "⚠️ Keyword is empty. "
                        + " Please enter an appropriate sentence."
                    )

            df = (
                DataFrame(keywords, columns=["Keyword", "Importance"])
                .sort_values(by="Importance", ascending=False)
                .reset_index(drop=True)
            )

            df.index += 1

            # Add styling
            cmGreen = sns.light_palette("green", as_cmap=True)
            cmRed = sns.light_palette("red", as_cmap=True)
            df = df.style.background_gradient(
                cmap=cmGreen,
                subset=[
                    "Importance",
                ],
            )

            c1, c2, c3 = st.columns([1, 3, 1])

            format_dictionary = {
                "Importance": "{:.1%}",
            }
            # model_load_state = st.info('👉 We are working on it...! 👀')
            df = df.format(format_dictionary)

            with c2:
                st.table(df)
            
            print('Keywords :',keywords)

            keywords_list = [] # ['peaceful']
            for a, b in keywords:
                keywords_list.append(a)
            
            keywords_in_music_tags = []
            for i in music_tags:
                if i in keywords_list:
                    keywords_in_music_tags.append(i)

            keywords_not_in_music_tags = [i for i in keywords_list if i not in keywords_in_music_tags]

            additional_keywords = {'action': ['leisure', 'outdoor', 'movement'], 'adventure': ['activity', 'explore', 'exploit'], 'advertising': ['marketing', 'advertisement'], 'ballad':['song', 'poem', 'poetic', 'lyrical', 'rainy', 'rain'],
                  'calm':['calming','breathe','comfortable','peaceful', 'quiet', 'still', 'restful', 'gentle', 'sleep', 'rest', 'concentrate', 'concentration','study', 'homework', 'exam', 'nap', 'siesta'], 
                   'children':['childhood', 'kid', 'kindergarten'], 'Christmas':['christmas', 'santa claus', 'ornament', 'Xmas', 'xmas', 'santa', 'carol'],
                  'commerical':['building', 'business', 'enterprise'], 'cool':['vibe', 'fashionable', 'modern', 'funky', 'waiting', 'driving', 'drive'], 'corporate':['work', 'collaborative', 'associated'], 'dark':['dim', 'night', 'gloomy', 'pessimistic', 'hopeless', 'cynical'], 'drama':['theater', 'performance', 'show', 'play'], 'emotional':['sensitivity', 'sensible', 'sensibility', 'sensitive', 'moood', 'emotion'],
                  'dream':['fantasy', 'vision'], 'energetic':['enthusiastic', 'passionatie', 'dynamic', 'live', 'active', 'vibrant', 'high-powered', 'running', 'jogging', 'housework', 'household', 'housekeeping', 'clean', 'cleaning'],
                  'epic':['poetic', 'epodic', 'lyrical'], 'fast':['speed', 'speedy', 'rapid', 'quickly', 'speedily', 'rapidly'], 'film':['video', 'cinema', 'movie'], 'fun':['joy', 'laugh', 'smile', 'pleasure', 'amusement', 'enjoyment', 'entertainment', 'excitement', 'jollification', 'enjoyable', 'playful', 'pleasing', 'bored', 'boring', 'dull', 'tedious', 'tiresome', 'wearisome', 'listless'],
                  'game':'arcade', 'groovy':['cheerful', 'editorial', 'fantastic', 'splendid', 'fabulous', 'sensational', 'chic', 'trendy', 'rhythmic'], 'holiday':['vacation', 'anniversary', 'birthday'], 'hopeful':'optimistic', 'inspiring':['inspiration','inspirational'],'love':['heart', 'hug', 'romance', 'tenderness', 'hearted'],
                  'meditative':['pray', 'thoughtful', 'yoga', 'pilates', 'daybreak', 'daydream', 'daydreaming', 'trance', 'musing', 'thinking', 'think'], 'melancholic':'dawn','melodic':['instrument',  'weekend', 'morning', 'sunday', 'saturday', 'melody', 'lyrics'], 'motivational':['quote', 'car', 'commute', 'subway', 'bus', 'train', 'commuting'], 'nature':'landscape', 'party':['birthday', 'celebrate', 'celebration', 'confetti'],
                  'positive':['bright', 'favorable', 'helpful', 'cheerful', 'promising', 'encouraging', 'stress', 'stressed'], 'powerful':['strong', 'intense','dynamic', 'vivid','crossfit', 'exercising'], 'relaxing':['lazy', 'sleep', 'moderate', 'temper', 'ease', 'loosen', 'lighten', 'lessen','bed', 'stretching'],'retro':['90s', 'vintage'], 'sad':['alone', 'depressed', 'depression', 'lonely', 'upset', 'unhappy', 'sorrowful', 'regretful', 'downcast', 'miserable', 'downhearted', 'down', 'despondent', 'disconsolate', 'despairing'],
                  'sexy':['lingerie', 'sensual'], 'soft':['smooth', 'velvet', 'silky'], 'soundscape':'sound', 'space':['galaxy', 'planet', 'universe'], 'sport':['exercise', 'fitness', 'gym', 'workout', 'play'],
                  'summer':['beach', 'pool', 'summertime', 'picnic'], 'trailer':'transportation', 'travel':['camping', 'advance', 'proceed', 'progress', 'move']}

            for i in keywords_not_in_music_tags:
                if i in additional_keywords:
                    print(i, 'is in the tag list')
                else:
                    print(i, 'is not in the tag list')

            keywords_in_additional_keywords = []
            check = []
            for i in keywords_not_in_music_tags:
                for k, v in additional_keywords.items():
                    for j in range(len(v)):
                        if i in v[j]:
                            print(i, 'is in the additional tag list')
                            print(i, 'is equivalent with', k)
                            check.append(i)
                            i = k ## additional tag의 key 값으로 치환해줌
                            keywords_in_additional_keywords.append(i)
                        else:
                            pass
            # print('Keywords in additional tags :', keywords_in_additional_keywords)

            keywords_not_in_additional_keywords = [i for i in keywords_not_in_music_tags if i not in check]
            # print('Keywords NOT in additional tags :', keywords_not_in_additional_keywords)

            aggregated_keywords= list(set(keywords_in_music_tags) | set(keywords_in_additional_keywords))
            if len(aggregated_keywords) != 0:
                pass
            else:
                imsi = 'calm'
                aggregated_keywords.append(imsi)

            genre_keywords = {'background':'easylistening','film':'soundtrack', 'melancholic':'ambient', 'children': 'soundtrack', 'relaxing': 'classical',
            'meditative': 'classical', 'cool': 'electronic', 'emotional': 'classical', 'documentary': 'soundtrack', 'love': 'pop', 
            'drama': 'soundtrack', 'adventure': 'orchestral', 'heavy': 'metal', 'dark': 'ambient', 'retro': 'pop', 'ballad': 'pop',
            'epic': 'classical', 'calm': 'classical', 'slow': 'experimental', 'energetic':'electronic', 'deep': 'house', 'inspiring':'easylistening',
            'soft': 'easylistening', 'space': 'electronic', 'fun': 'pop', 'horror': 'soundtrack', 'positive':'pop', 'happy':'pop', 'summer':'chillout',
            'dream':'ambient', 'romantic':'easylistening', 'sad':'classical', 'hopeful':'easylistening', 'motivational':'pop', 
            'uplifting': 'pop', 'party':'dance','mellow':'chillout', 'groovy':'pop', 'soundscape':'ambient', 'corporate':'pop', 
            'advertising':'soundtrack','sport':'rock', 'sexy':'lounge', 'fast':'electronic', 'nature':'ambient', 'commercial':'pop', 
            'funny':'dance','dramatic':'orchestral', 'holiday':'pop', 'ambiental':'soundtrack', 'christmas':'pop', 'game':'electronic', 
            'travel':'pop','powerful':'rock', 'upbeat':'hiphop', 'movie':'soundtrack', 'action':'rock', 'trailer':'trailer'}
                
            keywords_associated_genre = []
            for i in aggregated_keywords:
                for k, v in genre_keywords.items():
                    if i in k:
                        keywords_associated_genre.append(v)
                    else:
                        pass
            
            genre_aggregated_keywords= list(set(aggregated_keywords) | set(keywords_associated_genre))
            
            print("Extracted total keywords:", keywords_list)
            print('Original mood and theme keywords:', keywords_in_music_tags)
            print('Additional keywords (before substituted):', check)
            print('Additional keywords (after substituted):', keywords_in_additional_keywords)
            print('Aggregated keywords:', aggregated_keywords)
            print("Couldn't find matching keywords:", keywords_not_in_additional_keywords)
            print('The keyword related to the genre are:', keywords_associated_genre)
            print('Genre aggregated keywords are:', genre_aggregated_keywords)

            if len(keywords) > 0:
                st.info(f"**✔️You can add keywords for more accurate music search!**")
                            
                added_keywords = []

                tc1 = st.container()
                with tc1:
                    k = st.session_state.active_page + "_tc1"
                    options = st.multiselect("Select keywords", music_tags, key=k)
                    for i in range(len(options)):
                        name = options[i]
                        added_keywords.append(name)
                    print("Added keywords are:", added_keywords)

                final_aggregated_keywords= list(set(genre_aggregated_keywords) | set(added_keywords))
                if '-' in final_aggregated_keywords:
                    final_aggregated_keywords.remove('-')
                else:
                    pass
    
                st.experimental_set_query_params(path=save_path)
                st.button('NEXT', on_click=cb, args=(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords))

            else:
                st.warning(f"**Please describe the mood of the music you want to hear or the situation in which you need music. You cannot proceed to the next step if an appropriate sentence is not entered.**")
                

        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print(e)
            message_container = st.empty() 
            message = message_container.write('👉 Please, wait. We are working on it...! 👀')
            if message != '':
                message_container.empty()

## ------------------ 2nd trial ----------------------------
def text_page2(cb):
    # show frontend title 
    st.title("Let's find music!")
    st.markdown('✔️ STEP 1: Please select your preferred scenario from the three provided options.')
    scenario = st.radio(
    "Please select a scenario that you preferred the most.",
    ('Want to discover a new music.', 
    'Playing with a child.', 
    'Studying or working.'))
    if scenario == 'Want to discover a new music.':
        st.write("<span style='color:blue'>Example: soft and tranquil jazz music that is good to listen to as a background sound.</span>",unsafe_allow_html=True)
    elif scenario == 'Playing with a child.':
        st.write("<span style='color:blue'>Example: upbeat children's songs that I can play for my child.</span>",unsafe_allow_html=True)
    else: 
        st.write("<span style='color:blue'>Example: calm and peaceful classical music that is suitable for listening while working.</span>",unsafe_allow_html=True)
    # st.markdown("✔️ Please describe the mood of the music you want to hear or the situation where you need music. We recommend music based on the entered text.")
    st.markdown("✔️ STEP 2: Enter a short descriptive text that suits the chosen scenario to search for music. We will find music that matches the text you have typed.")
    st.markdown("✔️ STEP 3: After entering the text, click the button below and wait for a while until the next process.")
    st.markdown(hide_menu, unsafe_allow_html = True)
    st.write("---")
    save_path = st.experimental_get_query_params()['path'][0]

    # # 함수 콜백
    # if st.session_state.active_page == 'Page_1':
    #     length = scenario_selector(scenario1)
    # elif st.session_state.active_page == 'Page_3':
    #     length = scenario_selector(scenario2)
    # elif st.session_state.active_page == 'Page_5':
    #     length = scenario_selector(scenario3)

    # show imgs to be selected    
    selection = st.container()
    with selection:
        try:
            c1, c2, c3 = st.columns([0.07, 5, 0.07])
            with c1:

                @st.cache_resource
                # @st.cache(allow_output_mutation=True)
                def load_model():
                    return KeyBERT()

                kw_model = load_model()

            with c2:
                doc = st.text_area(
                    "Type the text below (max 500 words)",
                    height=100,
                )

                MAX_WORDS = 500
                import re
                res = len(re.findall(r"\w+", doc))
                if res > MAX_WORDS:
                    st.warning(
                        "⚠️ Your text contains "
                        + str(res)
                        + " words."
                        + " Only the first 500 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
                    )

                    doc = doc[:MAX_WORDS]
                    
                # submit_button = st.form_submit_button(label="✨ Get me the data!")
                submit_button = st.button('✨ Get me the keywords!')
            global stopwords
            stopwords = stopwords.words('english')
            stop_list = ["song", "songs", "music", "search", "retrieve", "listen", "hear"]
            stpwrd = nltk.corpus.stopwords.words('english')
            # entend()function is used to add custom stopwords 
            stpwrd.extend(stop_list)

            if not submit_button and 'keep_going2' not in st.session_state:
                st.session_state.keep_going2 = False
            else:
                st.session_state.keep_going2 = True
            
            if st.session_state.keep_going2 == False:
                st.stop()


            keywords = kw_model.extract_keywords(
                doc,
                keyphrase_ngram_range=(1, 1),
                use_mmr=False,
                stop_words=stpwrd, #StopWords
                top_n=5,
                # diversity=Diversity,
            )

            if len(keywords)==0:
                st.warning(
                        "⚠️ Keyword is empty. "
                        + " Please enter an appropriate sentence."
                    )

            df = (
                DataFrame(keywords, columns=["Keyword", "Importance"])
                .sort_values(by="Importance", ascending=False)
                .reset_index(drop=True)
            )

            df.index += 1

            # Add styling
            cmGreen = sns.light_palette("green", as_cmap=True)
            cmRed = sns.light_palette("red", as_cmap=True)
            df = df.style.background_gradient(
                cmap=cmGreen,
                subset=[
                    "Importance",
                ],
            )

            c1, c2, c3 = st.columns([1, 3, 1])

            format_dictionary = {
                "Importance": "{:.1%}",
            }
            # model_load_state = st.info('👉 We are working on it...! 👀')
            df = df.format(format_dictionary)

            with c2:
                st.table(df)
            
            print('Keywords :',keywords)

            keywords_list = [] # ['peaceful']
            for a, b in keywords:
                keywords_list.append(a)
            
            keywords_in_music_tags = []
            for i in music_tags:
                if i in keywords_list:
                    keywords_in_music_tags.append(i)

            keywords_not_in_music_tags = [i for i in keywords_list if i not in keywords_in_music_tags]

            additional_keywords = {'action': ['leisure', 'outdoor', 'movement'], 'adventure': ['activity', 'explore', 'exploit'], 'advertising': ['marketing', 'advertisement'], 'ballad':['song', 'poem', 'poetic', 'lyrical', 'rainy', 'rain'],
                  'calm':['tranquil', 'calming','breathe','comfortable','peaceful', 'quiet', 'still', 'restful', 'gentle', 'sleep', 'rest', 'concentrate', 'concentration','study', 'homework', 'exam', 'nap', 'siesta'], 
                   'children':['childhood', 'kid', 'kindergarten'], 'Christmas':['christmas', 'santa claus', 'ornament', 'Xmas', 'xmas', 'santa', 'carol'],
                  'commerical':['building', 'business', 'enterprise'], 'cool':['vibe', 'fashionable', 'modern', 'funky', 'waiting', 'driving', 'drive'], 'corporate':['work', 'collaborative', 'associated'], 'dark':['dim', 'night', 'gloomy', 'pessimistic', 'hopeless', 'cynical'], 'drama':['theater', 'performance', 'show', 'play'], 'emotional':['sensitivity', 'sensible', 'sensibility', 'sensitive', 'moood', 'emotion'],
                  'dream':['fantasy', 'vision'], 'energetic':['enthusiastic', 'passionatie', 'dynamic', 'live', 'active', 'vibrant', 'high-powered', 'running', 'jogging', 'housework', 'household', 'housekeeping', 'clean', 'cleaning'],
                  'epic':['poetic', 'epodic', 'lyrical'], 'fast':['speed', 'speedy', 'rapid', 'quickly', 'speedily', 'rapidly'], 'film':['video', 'cinema', 'movie'], 'fun':['joy', 'laugh', 'smile', 'pleasure', 'amusement', 'enjoyment', 'entertainment', 'excitement', 'jollification', 'enjoyable', 'playful', 'pleasing', 'bored', 'boring', 'dull', 'tedious', 'tiresome', 'wearisome', 'listless'],
                  'game':'arcade', 'groovy':['cheerful', 'editorial', 'fantastic', 'splendid', 'fabulous', 'sensational', 'chic', 'trendy', 'rhythmic'], 'holiday':['vacation', 'anniversary', 'birthday'], 'hopeful':'optimistic', 'inspiring':['inspiration','inspirational'],'love':['heart', 'hug', 'romance', 'tenderness', 'hearted'],
                  'meditative':['pray', 'thoughtful', 'yoga', 'pilates', 'daybreak', 'daydream', 'daydreaming', 'trance', 'musing', 'thinking', 'think'], 'melancholic':'dawn','melodic':['instrument',  'weekend', 'morning', 'sunday', 'saturday', 'melody', 'lyrics'], 'motivational':['quote', 'car', 'commute', 'subway', 'bus', 'train', 'commuting'], 'nature':'landscape', 'party':['birthday', 'celebrate', 'celebration', 'confetti'],
                  'positive':['bright', 'favorable', 'helpful', 'cheerful', 'promising', 'encouraging', 'stress', 'stressed'], 'powerful':['strong', 'intense','dynamic', 'vivid','crossfit', 'exercising'], 'relaxing':['lazy', 'sleep', 'moderate', 'temper', 'ease', 'loosen', 'lighten', 'lessen','bed', 'stretching'],'retro':['90s', 'vintage'], 'sad':['alone', 'depressed', 'depression', 'lonely', 'upset', 'unhappy', 'sorrowful', 'regretful', 'downcast', 'miserable', 'downhearted', 'down', 'despondent', 'disconsolate', 'despairing'],
                  'sexy':['lingerie', 'sensual'], 'soft':['smooth', 'velvet', 'silky'], 'soundscape':'sound', 'space':['galaxy', 'planet', 'universe'], 'sport':['exercise', 'fitness', 'gym', 'workout', 'play'],
                  'summer':['beach', 'pool', 'summertime', 'picnic'], 'trailer':'transportation', 'travel':['camping', 'advance', 'proceed', 'progress', 'move']}

            for i in keywords_not_in_music_tags:
                if i in additional_keywords:
                    print(i, 'is in the tag list')
                else:
                    print(i, 'is not in the tag list')

            keywords_in_additional_keywords = []
            check = []
            for i in keywords_not_in_music_tags:
                for k, v in additional_keywords.items():
                    for j in range(len(v)):
                        if i in v[j]:
                            print(i, 'is in the additional tag list')
                            print(i, 'is equivalent with', k)
                            check.append(i)
                            i = k ## additional tag의 key 값으로 치환해줌
                            keywords_in_additional_keywords.append(i)
                        else:
                            pass
            # print('Keywords in additional tags :', keywords_in_additional_keywords)

            keywords_not_in_additional_keywords = [i for i in keywords_not_in_music_tags if i not in check]
            # print('Keywords NOT in additional tags :', keywords_not_in_additional_keywords)

            aggregated_keywords= list(set(keywords_in_music_tags) | set(keywords_in_additional_keywords))
            if len(aggregated_keywords) != 0:
                pass
            else:
                imsi = 'calm'
                aggregated_keywords.append(imsi)

            genre_keywords = {'background':'easylistening','film':'soundtrack', 'melancholic':'ambient', 'children': 'soundtrack', 'relaxing': 'classical',
            'meditative': 'classical', 'cool': 'electronic', 'emotional': 'classical', 'documentary': 'soundtrack', 'love': 'pop', 
            'drama': 'soundtrack', 'adventure': 'orchestral', 'heavy': 'metal', 'dark': 'ambient', 'retro': 'pop', 'ballad': 'pop',
            'epic': 'classical', 'calm': 'classical', 'slow': 'experimental', 'energetic':'electronic', 'deep': 'house', 'inspiring':'easylistening',
            'soft': 'easylistening', 'space': 'electronic', 'fun': 'pop', 'horror': 'soundtrack', 'positive':'pop', 'happy':'pop', 'summer':'chillout',
            'dream':'ambient', 'romantic':'easylistening', 'sad':'classical', 'hopeful':'easylistening', 'motivational':'easylistening', 
            'uplifting': 'pop', 'party':'dance','mellow':'chillout', 'groovy':'pop', 'soundscape':'ambient', 'corporate':'pop', 
            'advertising':'soundtrack','sport':'rock', 'sexy':'lounge', 'fast':'electronic', 'nature':'ambient', 'commercial':'pop', 
            'funny':'dance','dramatic':'orchestral', 'holiday':'pop', 'ambiental':'soundtrack', 'christmas':'pop', 'game':'electronic', 
            'travel':'pop','powerful':'rock', 'upbeat':'hiphop', 'movie':'soundtrack', 'action':'rock', 'trailer':'trailer'}
                
            keywords_associated_genre = []
            for i in aggregated_keywords:
                for k, v in genre_keywords.items():
                    if i in k:
                        keywords_associated_genre.append(v)
                    else:
                        pass
            
            genre_aggregated_keywords= list(set(aggregated_keywords) | set(keywords_associated_genre))
            
            print("Extracted total keywords:", keywords_list)
            print('Original mood and theme keywords:', keywords_in_music_tags)
            print('Additional keywords (before substituted):', check)
            print('Additional keywords (after substituted):', keywords_in_additional_keywords)
            print('Aggregated keywords:', aggregated_keywords)
            print("Couldn't find matching keywords:", keywords_not_in_additional_keywords)
            print('The keyword related to the genre are:', keywords_associated_genre)
            print('Genre aggregated keywords are:', genre_aggregated_keywords)

            if len(keywords) > 0:
                st.info(f"**✔️You can add keywords for more accurate music search!**")
                            
                added_keywords = []

                tc2 = st.container()
                with tc2:
                    k = st.session_state.active_page + "_tc2"
                    options = st.multiselect("Select keywords", music_tags, key=k)
                    for i in range(len(options)):
                        name = options[i]
                        added_keywords.append(name)

                final_aggregated_keywords= list(set(genre_aggregated_keywords) | set(added_keywords))
                if '-' in final_aggregated_keywords:
                    final_aggregated_keywords.remove('-')
                else:
                    pass

                if 'children' in final_aggregated_keywords:
                    final_aggregated_keywords = ['children', 'fun']
                    print('Choose children scenario: changed final aggregated tags:', final_aggregated_keywords)

                st.experimental_set_query_params(path=save_path)
                st.button('NEXT', on_click=cb, args=(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords))

            else:
                st.warning(f"**Please describe the mood of the music you want to hear or the situation in which you need music. You cannot proceed to the next step if an appropriate sentence is not entered.**")
                

        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print(e)
            message_container = st.empty() 
            message = message_container.write('👉 Please, wait. We are working on it...! 👀')
            if message != '':
                message_container.empty()

## --------------------- 3rd trial ---------------------------
def text_page3(cb):
    # show frontend title 
    st.title("Let's find music!")
    st.markdown('✔️ STEP 1: Please select your preferred scenario from the three provided options.')
    scenario = st.radio(
    "Please select a scenario that you preferred the most.",
    ('Commuting to and from work.', 
    'While driving or before driving.', 
    'Emotional early morning hours.'))
    if scenario == 'Commuting to and from work.':
        st.write("<span style='color:blue'>Example: lyrical and melancholy song good to listen to on the way to work.</span>",unsafe_allow_html=True)
    elif scenario == 'While driving or before driving.':
        st.write("<span style='color:blue'>Example: good song to listen to while driving.</span>",unsafe_allow_html=True)
    else: 
        st.write("<span style='color:blue'>Example: a song to listen to when I greet a hopeful morning.</span>",unsafe_allow_html=True)
    # st.markdown("✔️ Please describe the mood of the music you want to hear or the situation where you need music. We recommend music based on the entered text.")
    st.markdown("✔️ STEP 2: Enter a short descriptive text that suits the chosen scenario to search for music. We will find music that matches the text you have typed.")
    st.markdown("✔️ STEP 3: After entering the text, click the button below and wait for a while until the next process.")
    st.markdown(hide_menu, unsafe_allow_html = True)
    st.write("---")
    save_path = st.experimental_get_query_params()['path'][0]


    # # 함수 콜백
    # if st.session_state.active_page == 'Page_1':
    #     length = scenario_selector(scenario1)
    # elif st.session_state.active_page == 'Page_3':
    #     length = scenario_selector(scenario2)
    # elif st.session_state.active_page == 'Page_5':
    #     length = scenario_selector(scenario3)

    # show imgs to be selected    
    selection = st.container()
    with selection:
        try:
            c1, c2, c3 = st.columns([0.07, 5, 0.07])
            with c1:

                @st.cache_resource  
                # @st.cache(allow_output_mutation=True)
                def load_model():
                    return KeyBERT()

                kw_model = load_model()

            with c2:
                doc = st.text_area(
                    "Type the text below (max 500 words)",
                    height=100,
                )

                MAX_WORDS = 500
                import re
                res = len(re.findall(r"\w+", doc))
                if res > MAX_WORDS:
                    st.warning(
                        "⚠️ Your text contains "
                        + str(res)
                        + " words."
                        + " Only the first 500 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
                    )

                    doc = doc[:MAX_WORDS]
                    
                # submit_button = st.form_submit_button(label="✨ Get me the data!")
                submit_button = st.button('✨ Get me the keywords!')
            global stopwords
            stopwords = stopwords.words('english')
            stop_list = ["song", "songs", "music", "search", "retrieve", "listen", "hear"]
            stpwrd = nltk.corpus.stopwords.words('english')
            # entend()function is used to add custom stopwords 
            stpwrd.extend(stop_list)

            if not submit_button and 'keep_going3' not in st.session_state:
                st.session_state.keep_going3 = False
            else:
                st.session_state.keep_going3 = True
            
            if st.session_state.keep_going3 == False:
                st.stop()

            keywords = kw_model.extract_keywords(
                doc,
                keyphrase_ngram_range=(1, 1),
                use_mmr=False,
                stop_words=stpwrd, #StopWords
                top_n=5,
                # diversity=Diversity,
            )

            if len(keywords)==0:
                st.warning(
                        "⚠️ Keyword is empty. "
                        + " Please enter an appropriate sentence."
                    )

            df = (
                DataFrame(keywords, columns=["Keyword", "Importance"])
                .sort_values(by="Importance", ascending=False)
                .reset_index(drop=True)
            )

            df.index += 1

            # Add styling
            cmGreen = sns.light_palette("green", as_cmap=True)
            cmRed = sns.light_palette("red", as_cmap=True)
            df = df.style.background_gradient(
                cmap=cmGreen,
                subset=[
                    "Importance",
                ],
            )

            c1, c2, c3 = st.columns([1, 3, 1])

            format_dictionary = {
                "Importance": "{:.1%}",
            }
            # model_load_state = st.info('👉 We are working on it...! 👀')
            df = df.format(format_dictionary)

            with c2:
                st.table(df)
            
            print('Keywords :',keywords)

            keywords_list = [] # ['peaceful']
            for a, b in keywords:
                keywords_list.append(a)
            
            keywords_in_music_tags = []
            for i in music_tags:
                if i in keywords_list:
                    keywords_in_music_tags.append(i)

            keywords_not_in_music_tags = [i for i in keywords_list if i not in keywords_in_music_tags]

            additional_keywords = {'action': ['leisure', 'outdoor', 'movement'], 'adventure': ['activity', 'explore', 'exploit'], 'advertising': ['marketing', 'advertisement'], 'ballad':['song', 'poem', 'poetic', 'lyrical', 'rainy', 'rain'],
                  'calm':['calming','breathe','comfortable','peaceful', 'quiet', 'still', 'restful', 'gentle', 'sleep', 'rest', 'concentrate', 'concentration','study', 'homework', 'exam', 'nap', 'siesta'], 
                   'children':['childhood', 'kid', 'kids', 'kindergarten'], 'Christmas':['christmas', 'santa claus', 'ornament', 'Xmas', 'xmas', 'santa', 'carol'],
                  'commerical':['building', 'business', 'enterprise'], 'cool':['vibe', 'fashionable', 'modern', 'funky', 'waiting', 'driving', 'drive'], 'corporate':['work', 'collaborative', 'associated'], 'dark':['dim', 'night', 'gloomy', 'pessimistic', 'hopeless', 'cynical'], 'drama':['theater', 'performance', 'show', 'play'], 'emotional':['sensitivity', 'sensible', 'sensibility', 'sensitive', 'moood', 'emotion'],
                  'dream':['fantasy', 'vision'], 'energetic':['enthusiastic', 'passionatie', 'dynamic', 'live', 'active', 'vibrant', 'high-powered', 'running', 'jogging', 'housework', 'household', 'housekeeping', 'clean', 'cleaning'],
                  'epic':['poetic', 'epodic', 'lyrical'], 'fast':['speed', 'speedy', 'rapid', 'quickly', 'speedily', 'rapidly'], 'film':['video', 'cinema', 'movie'], 'fun':['joy', 'laugh', 'smile', 'pleasure', 'amusement', 'enjoyment', 'entertainment', 'excitement', 'jollification', 'enjoyable', 'playful', 'pleasing', 'bored', 'boring', 'dull', 'tedious', 'tiresome', 'wearisome', 'listless'],
                  'game':'arcade', 'groovy':['cheerful', 'editorial', 'fantastic', 'splendid', 'fabulous', 'sensational', 'chic', 'trendy', 'rhythmic'], 'holiday':['vacation', 'anniversary', 'birthday'], 'hopeful':'optimistic', 'inspiring':['inspiration','inspirational'],'love':['heart', 'hug', 'romance', 'tenderness', 'hearted'],
                  'meditative':['pray', 'thoughtful', 'yoga', 'pilates', 'daybreak', 'daydream', 'daydreaming', 'trance', 'musing', 'thinking', 'think'], 'melancholic':'dawn','melodic':['instrument',  'weekend', 'morning', 'sunday', 'saturday', 'melody', 'lyrics'], 'motivational':['quote', 'car', 'commute', 'subway', 'bus', 'train', 'commuting'], 'nature':'landscape', 'party':['birthday', 'celebrate', 'celebration', 'confetti'],
                  'positive':['bright', 'favorable', 'helpful', 'cheerful', 'promising', 'encouraging', 'stress', 'stressed'], 'powerful':['strong', 'intense','dynamic', 'vivid','crossfit', 'exercising'], 'relaxing':['lazy', 'sleep', 'moderate', 'temper', 'ease', 'loosen', 'lighten', 'lessen','bed', 'stretching'],'retro':['90s', 'vintage'], 'sad':['alone', 'depressed', 'depression', 'lonely', 'upset', 'unhappy', 'sorrowful', 'regretful', 'downcast', 'miserable', 'downhearted', 'down', 'despondent', 'disconsolate', 'despairing'],
                  'sexy':['lingerie', 'sensual'], 'soft':['smooth', 'velvet', 'silky'], 'soundscape':'sound', 'space':['galaxy', 'planet', 'universe'], 'sport':['exercise', 'fitness', 'gym', 'workout', 'play'],
                  'summer':['beach', 'pool', 'summertime', 'picnic'], 'trailer':'transportation', 'travel':['camping', 'advance', 'proceed', 'progress', 'move']}

            for i in keywords_not_in_music_tags:
                if i in additional_keywords:
                    print(i, 'is in the tag list')
                else:
                    print(i, 'is not in the tag list')

            keywords_in_additional_keywords = []
            check = []
            for i in keywords_not_in_music_tags:
                for k, v in additional_keywords.items():
                    for j in range(len(v)):
                        if i in v[j]:
                            print(i, 'is in the additional tag list')
                            print(i, 'is equivalent with', k)
                            check.append(i)
                            i = k ## additional tag의 key 값으로 치환해줌
                            keywords_in_additional_keywords.append(i)
                        else:
                            pass
            # print('Keywords in additional tags :', keywords_in_additional_keywords)

            keywords_not_in_additional_keywords = [i for i in keywords_not_in_music_tags if i not in check]
            # print('Keywords NOT in additional tags :', keywords_not_in_additional_keywords)

            aggregated_keywords= list(set(keywords_in_music_tags) | set(keywords_in_additional_keywords))
            if len(aggregated_keywords) != 0:
                pass
            else:
                imsi = 'calm'
                aggregated_keywords.append(imsi)

            genre_keywords = {'background':'easylistening','film':'soundtrack', 'melancholic':'ambient', 'children': 'soundtrack', 'relaxing': 'classical',
            'meditative': 'classical', 'cool': 'electronic', 'emotional': 'classical', 'documentary': 'soundtrack', 'love': 'pop', 
            'drama': 'soundtrack', 'adventure': 'orchestral', 'heavy': 'metal', 'dark': 'ambient', 'retro': 'pop', 'ballad': 'pop',
            'epic': 'classical', 'calm': 'classical', 'slow': 'experimental', 'energetic':'electronic', 'deep': 'house', 'inspiring':'easylistening',
            'soft': 'easylistening', 'space': 'electronic', 'fun': 'pop', 'horror': 'soundtrack', 'positive':'pop', 'happy':'pop', 'summer':'chillout',
            'dream':'ambient', 'romantic':'easylistening', 'sad':'classical', 'hopeful':'easylistening', 'motivational':'pop', 
            'uplifting': 'pop', 'party':'dance','mellow':'chillout', 'groovy':'pop', 'soundscape':'ambient', 'corporate':'pop', 
            'advertising':'soundtrack','sport':'rock', 'sexy':'lounge', 'fast':'electronic', 'nature':'ambient', 'commercial':'pop', 
            'funny':'dance','dramatic':'orchestral', 'holiday':'pop', 'ambiental':'soundtrack', 'christmas':'pop', 'game':'electronic', 
            'travel':'pop','powerful':'rock', 'upbeat':'hiphop', 'movie':'soundtrack', 'action':'rock', 'trailer':'trailer'}
                
            keywords_associated_genre = []
            for i in aggregated_keywords:
                for k, v in genre_keywords.items():
                    if i in k:
                        keywords_associated_genre.append(v)
                    else:
                        pass
            
            genre_aggregated_keywords= list(set(aggregated_keywords) | set(keywords_associated_genre))
            
            print("Extracted total keywords:", keywords_list)
            print('Original mood and theme keywords:', keywords_in_music_tags)
            print('Additional keywords (before substituted):', check)
            print('Additional keywords (after substituted):', keywords_in_additional_keywords)
            print('Aggregated keywords:', aggregated_keywords)
            print("Couldn't find matching keywords:", keywords_not_in_additional_keywords)
            print('The keyword related to the genre are:', keywords_associated_genre)
            print('Genre aggregated keywords are:', genre_aggregated_keywords)

            if len(keywords) > 0:
                st.info(f"**✔️You can add keywords for more accurate music search!**")
                            
                added_keywords = []

                tc3 = st.container()
                with tc3:
                    k = st.session_state.active_page + "_tc3"
                    options = st.multiselect("Select keywords", music_tags, key=k)
                    for i in range(len(options)):
                        name = options[i]
                        added_keywords.append(name)
                    print("added keywords are:", added_keywords)
                    
                final_aggregated_keywords= list(set(genre_aggregated_keywords) | set(added_keywords))
                if '-' in final_aggregated_keywords:
                    final_aggregated_keywords.remove('-')
                else:
                    pass

                st.experimental_set_query_params(path=save_path)
                st.button('NEXT', on_click=cb, args=(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords))
                # if submitted:
                #     st.button('NEXT', on_click=cb, args=(save_path, scenario, doc, keywords, added_keywords, final_aggregated_keywords))

        
            else:
                st.warning(f"**Please describe the mood of the music you want to hear or the situation in which you need music. You cannot proceed to the next step if an appropriate sentence is not entered.**")
                

        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print(e)
            message_container = st.empty() 
            message = message_container.write('👉 Please, wait. We are working on it...! 👀')
            if message != '':
                message_container.empty()



## ------------------ for Mood Music Retrieval ------------------------    
def TagLoad(path):
    f = open(path)
    data = json.load(f)
    tags = data['submits'][-1]['Final aggregated keywords']  #tags = ['sad', 'calm', 'emotional']
    print('tags are', tags)
    music_tag = list(tags)
    return music_tag


mood_theme_list = ['background', 'film', 'melancholic', 'calm', 'melodic', 'children', 'relaxing', 'meditative', 'cool', 'documentary', 'emotional', 'space', 'love', 'drama', 
'adventure', 'heavy', 'dark', 'soft', 'energetic', 'retro', 'ballad', 'advertising', 'epic', 'action', 'dramatic', 'powerful', 'upbeat', 'inspiring', 'uplifting', 'soundscape', 'slow', 
'deep', 'fun', 'horror', 'nature', 'funny', 'happy', 'positive', 'summer', 'dream', 'romantic', 'sad', 'hopeful', 'mellow', 'motivational', 'party', 'groovy', 'corporate', 'sport', 'travel', 
'sexy', 'movie', 'fast', 'commercial', 'holiday', 'ambiental', 'christmas', 'game', 'trailer']

def music_retrieval():
    # remoteFilePath = '/nas2/epark/mtg-jamendo-dataset/data/autotagging_moodtheme.tsv'
    remoteFilePath = '/nas3/epark/workspace/IMR/autotagging_moodthemegenre.tsv' 
    localFilePath = 'autotagging_moodthemegenre.tsv'
    sftp.download(remoteFilePath, localFilePath)
    tracks, tags, extra = commons.read_file(localFilePath)

    find_tag_list = []
    save_path = st.experimental_get_query_params()['path'][0]
    print("save path: " + save_path)
    music_tag = TagLoad(save_path)
    for i in music_tag:
        if i in mood_theme_list:
            p = tags['mood/theme'][i]
            q = list(p)
            find_tag_list.extend(q)
            # print('length of find_tag_list', len(find_tag_list))
        else:
            p = tags['genre'][i]
            q = list(p)
            find_tag_list.extend(q)
    print('length of find_tag_list', len(find_tag_list))

    newlist = [] # empty list to hold unique elements from the list
    duplist = [] # empty list to hold the duplicate elements from the list
    for i in find_tag_list:
        if i not in newlist:
            newlist.append(i)
        else:
            duplist.append(i) # this method catches the first duplicate entries, and appends them to the list
    print('length of duplicated music:', len(duplist)) 

    random_all = random.choices(duplist, k=5)
    st.session_state['music_random'] = random_all
    for r in random_all:
        print(r) # for debug 
        

    
def createAudio(filename):
    remoteFilePath = sftp.dirRemoteMusicData + '/' + filename
    localFilePath = sftp.dirMusic + '/' + filename
    sftp.download(remoteFilePath, localFilePath)
    audio_file = open(localFilePath, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/ogg', start_time=0)

## streamlit display codes
def music_page(cb):
    st.title('Music Finder 🎵')
    st.subheader("Now, we find music lists that match the text!")
    st.caption('- The music searched in this study is a copyright-free sound sources provided for research purposes.')
    st.caption('- Therefore, we inform you that it may be different from the latest music you are familiar with.')
    st.write('-----')
    st.markdown("🎧 Please enjoy the music and answer the questions below. 🎧")
    st.caption("- Listen to music for at least 30 seconds and answer the question (slide bar) below.")
    st.markdown(hide_menu, unsafe_allow_html = True)

    random_all = st.session_state['music_random']
    for r in random_all:
        print(r) # for debug
        createAudio(str(r) + '.mp3')

    st.write('-----')

    ## save results
    with st.container():
        # satis_result = st.slider('Do you think the retrieved music represents the selected image well?', min_value=0, max_value=100, value=50, step=1)
        satis_result = st.select_slider('Overall, do you think the retrieved music matches the text you typed well?', options=['Strongly disagree', 'Disagree', 'Somewhat disagree', 'Neither agree nor disagree', 'Somewhat agree', 'Agree', 'Strongly agree'], value='Neither agree nor disagree')
        st.caption("- Note: Please evaluate how well the typed text represents the music, rather than providing a 'like' or 'dislike' rating for the provided music.")
        st.write('-----')
    
        save_path = st.experimental_get_query_params()['path'][0]
        with open(save_path, "r") as json_file:
            results_B = {'Music Satisfaction': satis_result}
            data = json.load(json_file)
            data['submits'][-1].update(results_B)

        with open(save_path, "w") as save_f:
            json.dump(data, save_f, ensure_ascii=False, indent=4)    
            print("exists, after", data)
        
        st.experimental_set_query_params(path=save_path)
        st.button('NEXT', on_click=cb)


## ------------------ for Survey ------------------------ 
def survey_page():
    save_path = st.experimental_get_query_params()['path'][0]
    print("path 5: " + save_path)
    st.title('Final survey')
    st.markdown("**This is the last step. Please answer the questions below.**")
    st.markdown("<span style='color:red'>An insincere response will be regarded as abandoning the experiment.  Please provide sincere responses until the end.</span>",unsafe_allow_html=True)
    st.caption("💪 You are almost there!")
    st.markdown(hide_menu, unsafe_allow_html = True)

    survey = st.container()
    with survey:
        st.write('-----')
        
        gender = st.radio(
            "What's your gender?",
            ('Male', 'Female', 'Non-binary/Third gender'))

        age = st.radio(
            "What's your age range?",
            ('20s', '30s', '40s', '50s', '60s', 'Above 60s'))

        education = st.radio(
            "What's the highest level of education that you have completed?",
            ('Less than high school', 'High school graduate', 'Some college', '2 year degree', '4 year degree', 'Professional degree', 'Doctorate'))
            # ('Primary/Elementary education not completed', 'Primary/Elementary education', 'Secondary education','Further education (Bachelor degree, diploma', 'Higher education (Masters, Doctorate)'))

        ethnicity = st.radio(
            "What's your ethnicity (or race)?",
            ('Prefer not to disclose', 'American Indigenous (Alaskan Native / Native American)', 'Asian', 'Black', 'Latinx / Hispanic', 'Middle Eastern / North African', 'Pacific Islander', 'White / Caucasian', 'Multi Race / Ethnicity'))

        service = st.text_input(
            "What service do you use to search for music? (Example: Spotify, YouTube Music)")

        if not service:
            st.warning("Please kindly provide a response to the question.")

        inconvenient = st.text_input(
            "What was the most inconvenient thing about searching for music using the music search service you answered above?")
        
        if not inconvenient:
            st.warning("Please kindly provide a response to the question.")
        st.write('-----')

        sus1 = st.radio(
            "Overall, I am satisfied with how easy it is to use this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus2 = st.radio(
            "It was simple to use this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))
        
        sus3 = st.radio(
            "I was able to complete the tasks and scenarios quickly using this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus4 = st.radio(
            "I felt comfortable using this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus5 = st.radio(
            "It was easy to learn to use this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))
        
        sus6 = st.radio(
            "I believe I could become productive quickly using this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus7 = st.radio(
            "The system gave error messages that clearly told me how to fix problems.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus8 = st.radio(
            "Whenever I made a mistake using the system, I could recover easily and quickly.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus9 = st.radio(
            "The information provided with this system was clear.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus10 = st.radio(
            "It was easy to find the information I needed.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus11 = st.radio(
            "The information was effective in helping me complete the tasks and scenarios.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus12 = st.radio(
            "The organization of information on the system screens was clear.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus13 = st.radio(
            "The interface of this system was pleasant.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus14 = st.radio(
            "I liked using the interface of this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus15 = st.radio(
            "This system has all the functions and capabilities I expect it to have.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        sus16 = st.radio(
            "Overall, I am satisfied with this system.",
            ('Strongly Agree', 'Agree', 'Somewhat Agree', 'Niether Agree Nor Disagree', 'Somewhat Disagree', 'Disagree', 'Strongly Disagree'))

        situation = st.text_input(
            "If this system becomes commercially available, in what situations do you think you will use it? (Example: When I want to listen to new music, but it is difficult to express my search terms in text.)")

        if not situation:
            st.warning("Please kindly provide a response to the question.")

        improved = st.text_input(
            "What aspects of the system you have used would you like to see improved?")

        if not improved:
            st.warning("Please kindly provide a response to the question.")
        st.write('-----')

        st.markdown('Please read the question and choices carefully before providing your answer.')
        
        ux1 = st.select_slider('Was the system obstructive or supportive?',options=['Obstructive: 0', 1, 2, 3, 4, 5, 6, 'Supportive: 7'], value=4)
        
        ux2 = st.select_slider('Was the system complicated or easy?',options=['Complicated: 0', 1, 2, 3, 4, 5, 6, 'Easy: 7'], value=4)
        
        ux3 = st.select_slider('Was the system inefficient or efficient?',options=['Inefficient: 0', 1, 2, 3, 4, 5, 6, 'Efficient: 7'], value=4)

        ux4 = st.select_slider('Was the system confusing or clear?',options=['Confusing: 0', 1, 2, 3, 4, 5, 6, 'Clear: 7'], value=4)

        ux5 = st.select_slider('Was the system boring or exciting?',options=['Boring: 0', 1, 2, 3, 4, 5, 6, 'Exciting: 7'], value=4)

        ux6 = st.select_slider('Was the system not interesting or interesting?',options=['Not interesting: 0', 1, 2, 3, 4, 5, 6, 'Interesting: 7'], value=4)

        ux7 = st.select_slider('Was the system conventional or inventive?',options=['Conventional: 0', 1, 2, 3, 4, 5, 6, 'Inventive: 7'], value=4)

        ux8 = st.select_slider('Was the system usual or leading edge?',options=['Usual: 0', 1, 2, 3, 4, 5, 6, 'Leading edge: 7'], value=4)

        
        
        # ux1 = st.select_slider('Did the system usage experience annoying you or was it enjoyable?', options=['Annoying: 0', 1, 2, 3, 4, 5, 6, 'Enjoyable: 7'], value=4)
 
        # ux2 = st.select_slider('Did you have trouble understanding how to use the system?',options=['Not understandable: 0', 1, 2, 3, 4, 5, 6, 'Understandable: 7'], value=4)

        # ux3 = st.select_slider('Was the system creative or dull?',options=['Creative: 0', 1, 2, 3, 4, 5, 6, 'Dull: 7'], value=4)
        
        # ux4 = st.select_slider('Was it easy or difficult to learn how to use the system?',options=['Easy to learn: 0', 1, 2, 3, 4, 5, 6, 'Difficult to learn: 7'], value=4)
        
        # ux5 = st.select_slider('Was the system valuable or inferior?',options=['Valuable: 0', 1, 2, 3, 4, 5, 6, 'Inferior: 7'], value=4)

        # ux6 = st.select_slider('Was the system boring or exciting?',options=['Boring: 0', 1, 2, 3, 4, 5, 6, 'Exciting: 7'], value=4)

        # ux7 = st.select_slider('Was the system not interesting or interesting?',options=['Not interesting: 0', 1, 2, 3, 4, 5, 6, 'Interesting: 7'], value=4)

        # ux8 = st.select_slider('Was the system unpredictable or predictable?',options=['Unpredictable: 0', 1, 2, 3, 4, 5, 6, 'Predictable: 7'], value=4)

        # ux9 = st.select_slider('Was the system fast or slow?',options=['Fast: 0', 1, 2, 3, 4, 5, 6, 'Slow: 7'], value=4)

        # ux10 = st.select_slider('Was the system inventive or conventional?',options=['Inventive: 0', 1, 2, 3, 4, 5, 6, 'Convnentional: 7'], value=4)

        # ux11 = st.select_slider('Was the system obstructive or supportive?',options=['Obstructive: 0', 1, 2, 3, 4, 5, 6, 'Supportive: 7'], value=4)

        # ux12 = st.select_slider('Was the system good or bad?',options=['Good: 0', 1, 2, 3, 4, 5, 6, 'Bad: 7'], value=4)

        # ux13 = st.select_slider('Was the system complicated or easy?',options=['Complicated: 0', 1, 2, 3, 4, 5, 6, 'Easy: 7'], value=4)

        # ux14 = st.select_slider('Did the system usage experience unlikable or was it pleasing?',options=['Unlikable: 0', 1, 2, 3, 4, 5, 6, 'Pleasing: 7'], value=4)

        # ux15 = st.select_slider('Was the system usual or leading edge?',options=['Usual: 0', 1, 2, 3, 4, 5, 6, 'Leading edge: 7'], value=4)

        # ux16 = st.select_slider('Did the system usage experience unpleasant or was it pleasant?',options=['Unpleasant: 0', 1, 2, 3, 4, 5, 6, 'Pleasant: 7'], value=4)

        # ux17 = st.select_slider('Was the system secure or not secure?',options=['Secure: 0', 1, 2, 3, 4, 5, 6, 'Not secure: 7'], value=4)

        # ux18 = st.select_slider('Was the experience of using the system motivating or demotivating?',options=['Motivating: 0', 1, 2, 3, 4, 5, 6, 'Demotivating: 7'], value=4)

        # ux19 = st.select_slider('Did the system usage experience meet your expectations or did it not meet your expectations?',options=['Meets expectations: 0', 1, 2, 3, 4, 5, 6, 'Does not meet expectations: 7'], value=4)

        # ux20 = st.select_slider('Was the system inefficient or efficient?',options=['Inefficient: 0', 1, 2, 3, 4, 5, 6, 'Efficient: 7'], value=4)

        # ux21 = st.select_slider('Was the system clear or confusing?',options=['Clear: 0', 1, 2, 3, 4, 5, 6, 'Confusing: 7'], value=4)

        # ux22 = st.select_slider('Was the system impractical or practical?',options=['Impractical: 0', 1, 2, 3, 4, 5, 6, 'Practical: 7'], value=4)

        # ux23 = st.select_slider('Was the system organized or cluttered?',options=['Organized: 0', 1, 2, 3, 4, 5, 6, 'Cluttered: 7'], value=4)

        # ux24 = st.select_slider('Was the system attractive or unattractive?',options=['Attractive: 0', 1, 2, 3, 4, 5, 6, 'Unattractive: 7'], value=4)

        # ux25 = st.select_slider('Was the system friendly or unfriendly?',options=['Friendly: 0', 1, 2, 3, 4, 5, 6, 'Unfriendly: 7'], value=4)

        # ux26 = st.select_slider('Was the system conservative or innovative?',options=['Conservative: 0', 1, 2, 3, 4, 5, 6, 'Innovative: 7'], value=4)


        id = st.session_state['id']
        st.text(f"Here is your ID: " + id)
        st.text('Copy this value to paste into MTurk.')
        st.text('When you have copied this ID, please click the check box below to submit your survey.')

        ## save results
        if st.checkbox("Do you want to move to the next page?", key='fin'):
            results_B = {'gender': gender, 'age': age, 'education': education, 'ethnicity': ethnicity,
             'service':service, 'inconvenient':inconvenient, 'sus1': sus1, 'sus2': sus2, 'sus3': sus3, 
             'sus4': sus4, 'sus5': sus5, 'sus6': sus6, 'sus7': sus7, 'sus8': sus8,'sus9': sus9,
             'sus10': sus10, 'sus11': sus11, 'sus12': sus12, 'sus13': sus13, 'sus14': sus14, 'sus15': sus15,
             'sus16': sus16, 'situation': situation, 'improved': improved,
             'ux1': ux1, 'ux2': ux2, 'ux3': ux3, 'ux4': ux4, 'ux5': ux5, 'ux6': ux6, 
             'ux7': ux7, 'ux8': ux8, 'workerID' : id
             }
            with open(save_path, "r") as json_file:
                data = {}
                data = json.load(json_file)
            data['submits'].append(results_B)

            with open(save_path, "w") as save_f:
                json.dump(data, save_f, ensure_ascii=False, indent=4)
                print("exists, after", data)
            
            id = st.session_state['id']
            sftp.upload(save_path, sftp.dirRemoteSurveyResult + '/' + id + ".json")
            st.button('END', on_click=CB_Page9)  
                                                



## ------------------ for Final ------------------------ 
def final_page():
    st.balloons()
    st.title("Thank you for your participation!")
    st.markdown(hide_menu, unsafe_allow_html = True)       

                                                
# run the active page
if st.session_state.active_page == 'Home':
    home()
elif st.session_state.active_page == 'Page_0':
    note()
elif st.session_state.active_page == 'Page_1':
    text_page1(CB_Page1)
elif st.session_state.active_page == 'Page_2':
    music_page(CB_Page2)
elif st.session_state.active_page == 'Page_3':
    text_page2(CB_Page3)
elif st.session_state.active_page == 'Page_4':
    music_page(CB_Page4)
elif st.session_state.active_page == 'Page_5':
    text_page3(CB_Page5)
elif st.session_state.active_page == 'Page_6':
    music_page(CB_Page6)
# elif st.session_state.active_page == 'Page_7':
#     text_page(theme_imgs2, CB_Page7)
# elif st.session_state.active_page == 'Page_8':
#     music_page(CB_Page8)
elif st.session_state.active_page == 'Page_9':
    survey_page()
elif st.session_state.active_page == 'Page_10':
    final_page()      