from memo_chat.models import Memory

RRF_K = 60.0


def rrf_merge(fts_results: list[Memory], vec_results: list[Memory]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for rank, m in enumerate(fts_results):
        scores[m.id] = scores.get(m.id, 0.0) + 1.0 / (RRF_K + float(rank + 1))
    for rank, m in enumerate(vec_results):
        scores[m.id] = scores.get(m.id, 0.0) + 1.0 / (RRF_K + float(rank + 1))
    return scores


def collect_mems(kw: list[Memory], vec: list[Memory]) -> dict[str, Memory]:
    mems: dict[str, Memory] = {}
    for m in kw:
        mems[m.id] = m
    for m in vec:
        if m.id not in mems:
            mems[m.id] = m
    return mems


def apply_type_weights(mems: dict[str, Memory], scores: dict[str, float]) -> None:
    for mid, m in mems.items():
        if m.memory_type == "pinned":
            scores[mid] *= 1.5


def sort_by_score(mems: dict[str, Memory], scores: dict[str, float]) -> list[Memory]:
    out = list(mems.values())
    out.sort(key=lambda m: scores.get(m.id, 0.0), reverse=True)
    return out


def paginate(
    results: list[Memory], offset: int, limit: int
) -> tuple[list[Memory], int]:
    total = len(results)
    if offset >= total:
        return [], total
    end = min(offset + limit, total)
    return results[offset:end], total
