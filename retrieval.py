import json
import pickle
from FlagEmbedding import FlagModel

class TextVectorRetriever:
    def __init__(self, model_path):
        self.model = FlagModel(model_path, query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：", use_fp16=True)
        self.abstract = []
        self.title = []
        self.link = []
        self.embeddings = []

    def save_embeddings(self, filename='embeddings.pkl'):
        package = {"title": self.title,"link": self.link, "abstract": self.abstract, "embeddings": self.embeddings}
        with open(filename, 'wb') as f:
            pickle.dump(package, f)

    def load_embeddings(self, filename='embeddings.pkl'):
        with open(filename, 'rb') as f:
            package = pickle.load(f)
        self.abstract = package['abstract']
        self.embeddings = package['embeddings']

    def extract_sentences_from_json(self, json_data):
        for item in json_data:
            abstract = item.get('Abstract', '')
            title = item.get('Title', '')
            link = item.get('ArXiv Link', '')

            if abstract:
                abstract = f"{abstract}"  # Combine title and abstract
                embedding = self.model.encode([abstract])
                self.abstract.append(abstract)
                self.title.append(title)
                self.link.append(link)
                self.embeddings.append(embedding)

    def calculate_similarity(self, query):
        result = []

        query_embedding = self.model.encode_queries([query])

        for i, sentence_embedding in enumerate(self.embeddings):
            similarity_score = query_embedding[0] @ sentence_embedding.T
            result.append((similarity_score, self.title[i], self.link[i]))

        return result

    @staticmethod
    def top_n_sentences(results, n):
        sorted_results = sorted(results, key=lambda x: x[0], reverse=True)
        return sorted_results[:n]

def main():
    retriever = TextVectorRetriever('BAAI/bge-small-zh-v1.5')

    # Assuming json_data contains the JSON data you provided
    with open('total_papers.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    retriever.extract_sentences_from_json(json_data)
    retriever.save_embeddings()

    retriever.load_embeddings()
    query = """The emergence of advanced neural networks has opened up new ways in automated code generation from conceptual models, promising to enhance software development processes. This paper presents a preliminary evaluation of GPT-4-Vision, a state-of-the-art deep learning model, and its capabilities in transforming Unified Modeling Language (UML) class diagrams into fully operating Java class files. In our study, we used exported images of 18 class diagrams comprising 10 single-class and 8 multi-class diagrams. We used 3 different prompts for each input, and we manually evaluated the results. We created a scoring system in which we scored the occurrence of elements found in the diagram within the source code. On average, the model was able to generate source code for 88% of the elements shown in the diagrams. Our results indicate that GPT-4-Vision exhibits proficiency in handling single-class UML diagrams, successfully transforming them into syntactically correct class files. However, for multi-class UML diagrams, the model's performance is weaker compared to single-class diagrams. In summary, further investigations are necessary to exploit the model's potential completely."""
    results = retriever.calculate_similarity(query)
    top_sentences = TextVectorRetriever.top_n_sentences(results, 3)

    for score, title, link in top_sentences:
        print(f"分数: {score}   标题: {title} 链接：{link}")

if __name__ == "__main__":
    main()
