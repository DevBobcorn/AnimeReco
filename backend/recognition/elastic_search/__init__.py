from elasticsearch import Elasticsearch

es_client = Elasticsearch("http://127.0.0.1:9200")


def store_feature(label, embedding, img_name):
    # 存储特征数据到es
    es_client.index(index="anime_face", body={
        "label": label,
        "embedding": embedding,
        "img_name": img_name
    })


# ES向量搜索
def feature_search(embedding):
    response = es_client.search(index="anime_face", body={
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": embedding
                    }
                }
            }
        }
    })
    res = []

    for face in response["hits"]["hits"]:
        res.append({
            "label": face["_source"]["label"],
            "score": face["_score"]
        })
    return res