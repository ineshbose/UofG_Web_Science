follow_ranges = {
    range(1): 0,
    range(1, 50): 0.5,
    range(50, 5000): 1.0,
    range(5000, 10000): 1.5,
    range(10000, 100000): 2.0,
    range(100000, 200000): 2.5,
}

age_ranges = {
    range(1): 0,
    range(1, 182): 0.5,
    range(182, 365): 1.0,
    range(365, 547): 1.5,
}

quote_ranges = {
    range(1): 0,
    range(1, 50): 0.5,
    range(50, 500): 1.0,
    range(500, 1000): 1.5,
}

reply_ranges = {
    range(1): 0,
    range(1, 5): 0.5,
    range(5, 15): 1.0,
    range(15, 30): 1.5,
}

retweet_ranges = {
    range(1): 0,
    range(1, 50): 0.5,
    range(50, 500): 1.0,
    range(500, 1000): 1.5,
    range(1000, 10000): 2.0,
    range(10000, 20000): 2.5,
}

favorite_ranges = {
    range(1): 0,
    range(1, 5): 0.5,
    range(5, 15): 1.0,
    range(15, 30): 1.5,
}


def get_weight(weight_type, **kwargs):
    return (
        (
            sum(
                (
                    (1.0 if kwargs.get("description") else 0),
                    (1.0 if kwargs.get("verified") else 0),
                    (
                        (
                            sum(
                                follow_ranges[k]
                                for k in follow_ranges
                                if kwargs.get("followers") in k
                            )
                            / 3
                        )
                        if kwargs.get("followers") in range(200000)
                        else 1.0
                    ),
                    (
                        (
                            sum(
                                age_ranges[k]
                                for k in age_ranges
                                if kwargs.get("account_age") in k
                            )
                            / 3
                        )
                        if kwargs.get("account_age") in range(547)
                        else 1.0
                    ),
                    (
                        (0.5 if not kwargs["defaults"][0] else 0)
                        + (0.5 if not kwargs["defaults"][1] else 0)
                        if kwargs.get("defaults") and len(kwargs.get("defaults")) == 2
                        else 0
                    ),
                )
            )
            / 5
        )
        if weight_type == "user"
        else (
            sum(
                (
                    (
                        (
                            sum(
                                quote_ranges[k]
                                for k in quote_ranges
                                if kwargs.get("quotes") in k
                            )
                            / 2
                        )
                        if kwargs.get("quotes") in range(1000)
                        else 1.0
                    ),
                    (
                        (
                            sum(
                                reply_ranges[k]
                                for k in reply_ranges
                                if kwargs.get("replies") in k
                            )
                            / 2
                        )
                        if kwargs.get("replies") in range(30)
                        else 1.0
                    ),
                    (
                        (
                            sum(
                                retweet_ranges[k]
                                for k in retweet_ranges
                                if kwargs.get("retweets") in k
                            )
                            / 3
                        )
                        if kwargs.get("retweets") in range(20000)
                        else 1.0
                    ),
                    (
                        (
                            sum(
                                favorite_ranges[k]
                                for k in favorite_ranges
                                if kwargs.get("favorites") in k
                            )
                            / 2
                        )
                        if kwargs.get("favorites") in range(30)
                        else 1.0
                    ),
                )
            )
            / 4
        )
    )
