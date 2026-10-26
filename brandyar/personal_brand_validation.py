import math
import statistics


def correlation(left, right):
    if len(left) < 5 or len(set(left)) < 2 or len(set(right)) < 2:
        return None
    return round(statistics.correlation(left, right), 4)


def summarize(rows, items):
    if len(rows) < 5:
        return {'sample_size': len(rows), 'correlations': [], 'internal_consistency': [], 'straight_line_count': sum(len(set(row.values())) == 1 for row in rows), 'warning': 'برای محاسبهٔ توصیفی حداقل پنج پاسخ کامل لازم است؛ این حد به معنای کفایت نمونهٔ پژوهشی نیست.'}
    correlations = []
    for index, item in enumerate(items):
        for other in items[index + 1:]:
            if item['dimension'] == other['dimension']:
                correlations.append({'left': item['id'], 'right': other['id'], 'value': correlation([row[item['id']] for row in rows], [row[other['id']] for row in rows])})
    consistency = []
    for dimension in dict.fromkeys(item['dimension'] for item in items):
        keys = [item['id'] for item in items if item['dimension'] == dimension]
        total_variance = statistics.variance([sum(row[key] for key in keys) for row in rows])
        alpha = len(keys) / (len(keys) - 1) * (1 - sum(statistics.variance([row[key] for row in rows]) for key in keys) / total_variance) if total_variance and len(keys) > 1 else None
        consistency.append({'dimension': dimension, 'alpha': round(alpha, 4) if alpha is not None and math.isfinite(alpha) else None})
    return {'sample_size': len(rows), 'correlations': correlations, 'internal_consistency': consistency, 'straight_line_count': sum(len(set(row.values())) == 1 for row in rows), 'warning': 'آمار توصیفی مقدماتی؛ پاسخ یکنواخت به معنای تقلب نیست. آلفا یا هم‌بستگی به‌تنهایی روایی یا پایایی ابزار را تأیید نمی‌کند.'}
