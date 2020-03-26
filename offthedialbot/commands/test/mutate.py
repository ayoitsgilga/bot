"""$test mutate"""
from offthedialbot import utils


async def main(ctx):
    profiles = utils.dbh.profiles.find({})

    ps = []
    mps = []

    for profile in profiles:

        ps.append({
            "_id": profile["_id"],
            "IGN": profiles["status"]["IGN"],
            "SW": profiles["status"]["SW"],
            "Ranks": profiles["status"]["Ranks"],
            "stylepoints": profiles["stylepoints"],
            "cxp": profiles["cxp"],
            "signal": profiles["signal_strength"],
        })
        mps.append({
            "_id": profiles["_id"],
            "banned": profile["meta"]["banned"],
            "smashgg": profile["meta"]["smashgg"],
            "reg": {
                "reg": profile["meta"]["competing"],
                "code": profile["meta"]["confirmation_code"],
            }
        })
    utils.dbh.profiles.remove({})
    utils.dbh.metaprofiles.remove({})
    utils.dbh.profiles.insert_many(ps)
    utils.dbh.metaprofiles.insert_many(mps)
