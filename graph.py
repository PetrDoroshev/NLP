from navec import Navec
from slovnet import Syntax
from slovnet.token import Token
from ipymarkup import show_dep_ascii_markup as show_markup
from slovnet import Morph
from natasha import MorphVocab
import json
from deeppavlov import build_model

navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
syntax = Syntax.load('slovnet_syntax_news_v1.tar')
syntax.navec(navec)

morph_vocab = MorphVocab()
morph = Morph.load('./slovnet_morph_news_v1.tar', batch_size=4)
morph.navec(navec)

#model = build_model("ru_syntagrus_joint_parsing", download=True, install=True)

def extract_triplets_slovnet(tokens):

    # Морфологический анализ
    morph_markup = morph(tokens)
    morph_dict = dict(zip(morph_markup.words, morph_markup.tokens))

    # Синтаксический анализ
    doc = syntax(tokens)


    # Построение словаря токенов по id для быстрого доступа
    token_dict = {token.id: token for token in doc.tokens}

    triplets = []

    # 1. Находим все глаголы (потенциальные действия)
    verbs = [token for token in doc.tokens if morph_dict[token.text].pos == 'VERB']

    for verb in verbs:
        subject = None
        obj = None
        action = verb.text

        # 2. Обработка отрицаний
        neg = next((t for t in doc.tokens
                    if t.head_id == verb.id and t.rel == 'neg'), None)
        if neg:
            action = 'не ' + action

        # 3. Поиск субъекта и объекта
        children = [t for t in doc.tokens if t.head_id == verb.id]

        # Основные конструкции
        for child in children:
            # Активный залог
            if child.rel == 'nsubj':
                subject = child.text

            # Пассивный залог
            elif child.rel == 'nsubj:pass':
                obj = child.text
                # Поиск агента в пассивной конструкции
                agent = next((t for t in doc.tokens
                              if t.head_id == verb.id and t.rel == 'obl:agent'), None)
                if agent:
                    subject = agent.text

            # Прямое дополнение
            elif child.rel == 'obj':
                obj = child.text

            # Предложное дополнение
            elif child.rel == 'obl':
                obj = child.text # Можно добавить обработку предлога

            # Составное сказуемое (инфинитив)
            elif child.rel == 'xcomp' and morph_dict[child.text].pos == 'VERB':
                action = child.text
                # Ищем новый объект для инфинитива
                new_obj = next((t for t in doc.tokens
                                if t.head_id == child.id and t.rel == 'obj'), None)
                if new_obj:
                    obj = new_obj.text

            # Придаточные предложения
            elif child.rel == 'acl:relcl':
                # Главное слово становится объектом
                obj = token_dict[child.head_id].text
                # В придаточном ищем подлежащее
                new_subj = next((t for t in doc.tokens
                                 if t.head_id == child.id and t.rel == 'nsubj'), None)
                if new_subj:
                    subject = new_subj.text

        # 4. Атрибутивные конструкции (nmod)
        if not subject and not obj:
            for child in children:
                if child.rel == 'nmod':
                    subject = token_dict[child.head_id].text
                    obj = child.text
                    action = 'имеет'  # Обобщенное действие

        # 5. Добавление триплета, если найдены все компоненты
        if subject and obj:
            triplets.append((subject, action, obj))

        # 6. Обработка однородных членов (conj)
    additional_triplets = []
    for subj, action, obj in triplets:
        # Проверяем, есть ли у объекта однородные члены
        obj_token = next((t for t in doc.tokens if t.text == obj), None)
        if obj_token:
            conj_objs = [t for t in doc.tokens
                         if t.head_id == obj_token.id and t.rel == 'conj']
            for conj in conj_objs:
                additional_triplets.append((subj, action, conj.text))

    triplets.extend(additional_triplets)

    return triplets


with open('./preprocessing_data/Токенизация/Книга Керамика ZrO2_tokenized.json', encoding="utf-8") as json_file:
    data = json.load(json_file)

    for p in data["tokens"]:
        for s in p:
            if len(s) > 0:
                triplets = extract_triplets_slovnet(s)
                if triplets: print(triplets)
