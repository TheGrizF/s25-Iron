from database.models import TasteProfile, TasteComparison
from database import db

def updateAllTasteComparisons():
    allUsers = TasteProfile.query.with_entities(TasteProfile.userID).all()

    for user in allUsers:
        updateTasteComparisons(user.userID)
    
    print("Taste Comparisons initialized")

def updateTasteComparisons(currID):
    # Get user and make sure user exists
    currUser = TasteProfile.query.filter_by(userID=currID).first()
    if not currUser:
        return
    
    # Get all other users to compare with
    otherUsers = TasteProfile.query.filter(TasteProfile.userID != currID).all()

    # Iterate through and get differences
    # Consider weighted differences.  If > 2, add more?
    for nextUser in otherUsers:
        compareToID = nextUser.userID

        values = [
            abs(currUser.sweet - nextUser.sweet),
            abs(currUser.spicy - nextUser.spicy),
            abs(currUser.sour - nextUser.sour),
            abs(currUser.bitter - nextUser.bitter),
            abs(currUser.umami - nextUser.umami),
            abs(currUser.savory - nextUser.savory)
        ]
        totalTaste = sum(values)

        # add allergen / diet check here? or in display

        # Add to table, check if comparison already exists and update

        exists = TasteComparison.query.filter_by(compareFrom=currID, compareTo=compareToID).first()

        if exists:
            exists.comparisonNum = totalTaste
        else:
            newEntry = TasteComparison(
                compareFrom = currID,
                compareTo = compareToID,
                comparisonNum = totalTaste
            )
            db.session.add(newEntry)
    
    db.session.commit()
    