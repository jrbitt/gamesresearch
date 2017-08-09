db.games.aggregate([
    {$group: { 
        _id: {nome: "$name"},
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