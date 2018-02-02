

def merge_similar(communities, threshold = 0.75):

    merged_communities = {}
    for community_name, members in communities.items():
        if len(merged_communities) == 0:
            merged_communities[community_name] = members
            continue

        to_merge = False
        to_merge_community_name = None
        for merged_community_name, merged_community_members in merged_communities.items():
            if len(merged_community_members) == 0 or len(members) == 0:
                continue
            intersection = merged_community_members & members
            if len(intersection) / min(len(merged_community_members), len(members)) >= threshold:
                to_merge = True
                to_merge_community_name = merged_community_name

        if to_merge:
            merged_communities[to_merge_community_name].update(members)
        else:
            merged_communities[community_name] = members

    return merged_communities
