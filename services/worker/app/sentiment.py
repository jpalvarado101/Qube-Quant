from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

_tok = AutoTokenizer.from_pretrained("ProsusAI/finbert")
_mod = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").eval()
def score_headlines(headlines: list[str]) -> tuple[float,float,float]:
    if not headlines: return 0.0, 0.5, 0.5
    with torch.no_grad():
        inp = _tok(headlines, return_tensors='pt', padding=True,truncation=True)
        logits = _mod(**inp).logits
        probs = torch.softmax(logits, dim=1).mean(0).cpu().numpy()
    neg, neu, pos = probs.tolist()
    sentiment = pos - neg # [-1,1]
    return float(sentiment), float(pos), float(neg)