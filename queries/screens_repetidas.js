db.screens.aggregate([
    {$group: { 
        _id: {codigo: "$code"},
        uniqueIds: {$addToSet: "$_id"},
        count: {$sum: 1}
        } 
    },
    {$match: { 
        count: {"$gt": 1}
        }
    },
    {$sort: {
        count: -1
        }
    }
]);  