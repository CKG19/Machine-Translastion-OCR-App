from transformers import MarianMTModel, MarianTokenizer
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AutoTokenizer
from nltk.tokenize import sent_tokenize
from nltk.tokenize import LineTokenizer
import math


class MyMTLModels:
    def __init__(self):
        pass

    def translate_with_marian_mt(self, input_text:str):
        model_path = '..\Machine Learning\model\opus-mt-en-id-4'
        tokenizer = MarianTokenizer.from_pretrained(model_path)
        model = MarianMTModel.from_pretrained(model_path)
        model = model.cuda()

        lt = LineTokenizer()
        batch_size = 8

        paragraphs = lt.tokenize(input_text)
        print(paragraphs)

        translated_paragraphs = []
        prefix = ">>ind<< "

        for paragraph in paragraphs:
            sentences = sent_tokenize(paragraph)
            batches = math.ceil(len(sentences) / batch_size)
            translated = []
            for i in range(batches):
                sent_batch = sentences[i*batch_size:(i+1)*batch_size]
                batch_with_prefix = [prefix + item.lower() for item in sent_batch]
                # print("sent_batch: ", batch_with_prefix)
                # print(len(batch_with_prefix))
                model_inputs = tokenizer(batch_with_prefix, return_tensors="pt", padding=True, truncation=True, max_length=500).to('cuda')
                translated_batch = model.generate(**model_inputs)
                translated += translated_batch
            translated = tokenizer.batch_decode(translated, skip_special_tokens=True)
            translated_paragraphs += ["\n".join(translated)]

        translated_text = "\n".join(translated_paragraphs)

        return translated_text
    
    def translate_with_bart(self, input_text:str):
        model_path = '..\Machine Learning\model\mbart-large-50-5'
        tokenizer = MBart50TokenizerFast.from_pretrained(model_path,src_lang="en_XX")
        model = MBartForConditionalGeneration.from_pretrained(model_path)
        model = model.cuda()

        lt = LineTokenizer()
        batch_size = 8

        paragraphs = lt.tokenize(input_text)
        translated_paragraphs = []

        for paragraph in paragraphs:
            sentences = sent_tokenize(paragraph)
            batches = math.ceil(len(sentences) / batch_size)
            translated = []
            for i in range(batches):
                sent_batch = sentences[i*batch_size:(i+1)*batch_size]
                model_inputs = tokenizer(sent_batch, return_tensors="pt", padding=True, truncation=True, max_length=500).to('cuda')
                translated_batch = model.generate(**model_inputs, forced_bos_token_id=tokenizer.lang_code_to_id["id_ID"])
                translated += translated_batch
            translated = tokenizer.batch_decode(translated, skip_special_tokens=True)
            translated_paragraphs += [" ".join(translated)]

        translated_text = "\n".join(translated_paragraphs)
        return translated_text
    
    def translate_with_t5(self, input_text:str):
        model_path = '..\\Machine Learning\\model\\flan-t5-finetuned-2'
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = T5ForConditionalGeneration.from_pretrained(model_path)
        model = model.cuda()

        lt = LineTokenizer()
        batch_size = 8

        paragraphs = lt.tokenize(input_text)
        translated_paragraphs = []
        prefix = "translate to Indonesia: "

        for paragraph in paragraphs:
            sentences = sent_tokenize(paragraph)
            batches = math.ceil(len(sentences) / batch_size)
            translated = []
            for i in range(batches):
                sent_batch = sentences[i*batch_size:(i+1)*batch_size]
                batch_with_prefix = [prefix + item.lower() for item in sent_batch]
                print("sent_batch: ", batch_with_prefix)
                print(len(batch_with_prefix))
                model_inputs = tokenizer(batch_with_prefix, return_tensors="pt", padding=True, max_length=500).to('cuda')
                translated_batch = model.generate(**model_inputs, max_new_tokens=512)
                translated += translated_batch
            translated = tokenizer.batch_decode(translated, skip_special_tokens=True)
            translated_paragraphs += [" ".join(translated)]

        translated_text = "\n".join(translated_paragraphs)
        return translated_text