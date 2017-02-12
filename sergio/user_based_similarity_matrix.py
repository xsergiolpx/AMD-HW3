from export_import_tools import *
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, find
import numpy as np

A = import_matrix("utility_matrix")
total_users = A.shape[0]
total_books = A.shape[1]

#books = ["0195153448", "0094770506", "1883219116"]

#Harry Potter books
books = [ "0439567610", "0747545111", "0613496744", "0312282540"]

# Pippi books
#books = ["0140309578", "0140327738", "0140309586", "0140309594", "0590016555"]

# Narnia
#books = ["0590257889", "0020444206", "0590257889", "0020444303", "0020444907"]

#Load the list of books
books_to_index = import_dic("books_to_index")
index_to_books = import_dic("index_to_books")

# Change them to indices
books_j = []
for book in books:
    try:
        books_j.append(books_to_index[book])
    except KeyError:
        print(book, "not found in database")
    #books_j = [books_to_index[book] for book in books]



#print(books_j)

# Create vector of 10 because the book is liked a lot
scores_list = np.repeat(10, len(books_j))

# same for user
users_i = np.repeat(0, len(books_j))

# create new matrix of the new user
B = csr_matrix((scores_list, (users_i, books_j)), shape=(1, total_books))

# calculate the similarity
similarity = cosine_similarity(A,B, dense_output=False)

#print(similarity)

# put in array form
similarity_users_index, _, similarity_score = find(similarity)

# find the indices (inside the array) of the maximum 5 similarities
number_of_similar_users = min(len(similarity_score), 5)
#print(similarity_score)

ind = np.argpartition(similarity_score, -number_of_similar_users)[-number_of_similar_users:]

# find the index of those users
similar_users_real_index = similarity_users_index[ind]

# Create a dict pf the type: {book_index1: [rating1, rating2]}
recommendations = {}
for j in range(len(similar_users_real_index)):
    i = similar_users_real_index[j]
    # sim is the normalized similitude of the user
    sim = similarity_score[ind][j]/max(similarity_score)
    _, similar_books_index, similar_books_rating = find(A[i])
    #normalize the rating of the book and add the sim
    similar_books_rating = (sim+similar_books_rating/10)/2
    # create the dict
    for j in range(len(similar_books_index)):
        if similar_books_index[j] not in books_j:
            if recommendations.get(similar_books_index[j]) != None:
                recommendations[similar_books_index[j]].append(similar_books_rating[j])
            else:
                recommendations[similar_books_index[j]] = [similar_books_rating[j]]

# Modify the dict to get the average of the books ratings
for book in recommendations:
    recommendations[book] = np.median(recommendations[book]) + len(recommendations[book])**0.5


# sort books by best
import operator
sorted_recommendations = sorted(recommendations.items(), key=operator.itemgetter(1), reverse=True)


# Load isbn to book title:
isbn_to_book = import_dic("isbn_to_books")

# Show read books:
print("\n--- You like:")
for book in books_j:
    print(isbn_to_book[index_to_books[book]])

print("\n--- Then you might like:")

counter = 1
for i in range(len(sorted_recommendations)):
    if counter > 5:
        break
    book_index = sorted_recommendations[i][0]
    try:
        isbn = index_to_books[book_index]
        recommended_book = isbn_to_book[isbn]
        print(recommended_book, "(pseudoscore", round(sorted_recommendations[i][1],2), ")")
        counter += 1
    except KeyError:
        pass