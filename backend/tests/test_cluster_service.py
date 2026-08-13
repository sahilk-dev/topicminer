from app.services.cluster import cluster_labels

def test_cluster_labels_empty_list():
    assert cluster_labels([]) == []

def test_cluster_labels_single_label():
    result = cluster_labels(["do a Q&A"])
    assert result == [0]