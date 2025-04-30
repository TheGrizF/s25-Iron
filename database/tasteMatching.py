from database.models.taste_profiles import tasteProfile
from database.models.user import tasteComparisons
from database import db

def updateAllTasteComparisons():
    allUsers = tasteProfile.query.with_entities(tasteProfile.user_id).all()

    for user in allUsers:
        updateTasteComparisons(user.user_id)
    
    print("Taste Comparisons initialized")

def updateTasteComparisons(currID):
    # Get user and make sure user exists
    currUser = tasteProfile.query.filter_by(user_id=currID).first()
    if not currUser:
        return
    
    # Get all other users to compare with
    otherUsers = tasteProfile.query.filter(tasteProfile.user_id != currID).all()

    # Iterate through and get differences
    # Consider weighted differences.  If > 2, add more?
    for nextUser in otherUsers:
        compareToID = nextUser.user_id

        values = [
            abs(currUser.sweet - nextUser.sweet),
            abs(currUser.spicy - nextUser.spicy),
            abs(currUser.sour - nextUser.sour),
            abs(currUser.bitter - nextUser.bitter),
            abs(currUser.umami - nextUser.umami),
            abs(currUser.savory - nextUser.savory)
        ]
        totalTaste = sum([v ** 1.5 for v in values])

        # add allergen / diet check here? or in display

        # Add to table, check if comparison already exists and update

        exists = tasteComparisons.query.filter_by(compare_from=currID, compare_to=compareToID).first()

        if exists:
            exists.comparison_num = totalTaste
        else:
            newEntry = tasteComparisons(
                compare_from = currID,
                compare_to = compareToID,
                comparison_num = totalTaste
            )
            db.session.add(newEntry)
    
    db.session.commit()
