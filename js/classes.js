class Item{
    constructor(name, link) {
        this.name = name;
        this.link = link;
    }
}


Item.prototype.toString = function() {
    return this.name + ", " + this.link;
}


class Bookshelf{
    constructor(item2tags, tag2items, word2items){
        this.item2tags = item2tags;
        this.tag2items = tag2items;
        this.word2items = word2items;
    }

}

Bookshelf.prototype.getItemsFromTag = function (tag) {
    if (!(this.tag2items.has(tag))){
        return [];
    }
    return this.tag2items.get(tag);
};

Bookshelf.prototype.getItemsFromWord = function (word) {
    if (!(this.word2items.has(word))) {
        return new Set();
    }
    return this.word2items.get(word);
};
