#import matplotlib as mpl
#mpl.use('Agg')
import collections
import glob
import os
import pickle
import sys
import re
import numpy 
import tensorflow as tf
import string
from tensorflow.python.ops.math_ops import tanh
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


#from mxnet import nd, autograd, gluon
#regex = re.compile('[%s]' % re.escape(string.punctuation))
DATA_FORMAT_NHWC='NHWC'


def isValid(word):
    word.strip()
    re.sub('[^A-Za-z]+', '', word)
    if word.isalpha():
        return True
    return False

def GetInputFiles():
    return glob.glob(os.path.join(sys.argv[1], '*/*/*/*.txt'))

VOCABULARY = collections.Counter()


# ** TASK 1.
def Tokenize(comment):
    """Receives a string (comment) and returns array of tokens."""
    
    wordset=set()
    comment=comment.lower()
    words=re.split('[^a-zA-Z]',comment)
    
    
    for i in range(0, len(words)):
        if isValid(words[i]) and len(words[i])>=2:
            wordset.add(words[i])
    
    return wordset   
      

# ** TASK 2.
def FirstLayer(net, l2_reg_val, is_training):
    """First layer of the neural network.

    Args:
        net: 2D tensor (batch-size, number of vocabulary tokens),
        l2_reg_val: float -- regularization coefficient.
        is_training: boolean tensor.A

    Returns:
        2D tensor (batch-size, 40), where 40 is the hidden dimensionality.
    """

    #print(net)
    x=tf.norm(net)
    
    reg_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)

    net = tf.contrib.layers.fully_connected(net, 40,weights_regularizer=None,biases_initializer=None,activation_fn=None)
    #print(net)

    
    m=tf.math.divide(
    net,
    x
    )
    
    m=tf.norm(m)
    
    m=tf.math.square(
    m
    )
    
    loss=tf.math.scalar_mul(
    l2_reg_val,
    m
    )
    
    tf.losses.add_loss(loss,loss_collection=tf.GraphKeys.REGULARIZATION_LOSSES)

    
    net=tf.nn.l2_normalize(net,axis=1)
    
    net=tf.contrib.layers.batch_norm(
    net,
    decay=0.999,
    center=True,
    scale=False,
    epsilon=0.001,
    activation_fn=None,
    param_initializers=None,
    param_regularizers=None,
    updates_collections=tf.GraphKeys.UPDATE_OPS,
    is_training=is_training,
    reuse=None,
    variables_collections=None,
    outputs_collections=None,
    trainable=True,
    batch_weights=None,
    fused=None,
    data_format=DATA_FORMAT_NHWC,
    zero_debias_moving_mean=False,
    scope=None,
    renorm=False,
    renorm_clipping=None,
    renorm_decay=0.99,
    adjustment=None
    )
    #print(net.dtype)
    net=tf.math.tanh(net)
    #print(net)
    
    return net


# ** TASK 2 ** BONUS part 1
def EmbeddingL2RegularizationUpdate(embedding_variable, net_input, learn_rate, l2_reg_val):
    """Accepts tf.Variable, tensor (batch_size, vocab size), regularization coef.
    Returns tf op that applies one regularization step on embedding_variable."""
    # TODO(student): Change this to something useful. Currently, this is a no-op.
    rate=2*learn_rate*l2_reg_val
    
    norm_input=tf.nn.l2_normalize(net_input,1)
    
    transpose_net=tf.transpose(norm_input)
    
    val=tf.matmul(norm_input,embedding_variable)

    t_val=tf.matmul(transpose_net,val)

    loss=tf.scalar_mul(rate,t_val)
    
    embedding_variable=embedding_variable - loss
    
    return embedding_variable


# ** TASK 2 ** BONUS part 2
def EmbeddingL1RegularizationUpdate(embedding_variable, net_input, learn_rate, l1_reg_val):
    """Accepts tf.Variable, tensor (batch_size, vocab size), regularization coef.
    Returns tf op that applies one regularization step on embedding_variable."""
    # TODO(student): Change this to something useful. Currently, this is a no-op.
    rate=learn_rate*l1_reg_val

    norm_input=tf.nn.l2_normalize(net_input,1)
    
    transpose_net=tf.transpose(norm_input)
    
    val=tf.matmul(norm_input,embedding_variable)

    t_val=tf.matmul(transpose_net,tf.math.sign(val))

    
    loss=tf.scalar_mul(rate,t_val)
    
    embedding_variable=embedding_variable - loss
    
    return embedding_variable


# ** TASK 3
def SparseDropout(slice_x, keep_prob=0.5):
 
    i,j = numpy.nonzero(slice_x)
    final_prob=(1-keep_prob) * len(i)
    index = numpy.random.choice(len(i), int(numpy.floor(final_prob)), replace=False)
    slice_x[i[index], j[index]]=0;

    return slice_x        

    


# ** TASK 4
# TODO(student): YOU MUST SET THIS TO GET CREDIT.
# You should set it to tf.Variable of shape (vocabulary, 40).
EMBEDDING_VAR = None


# ** TASK 5
# This is called automatically by VisualizeTSNE.
def ComputeTSNE(embedding_matrix):
    """Projects embeddings onto 2D by computing tSNE.
    
    Args:
        embedding_matrix: numpy array of size (vocabulary, 40)

    Returns:
        numpy array of size (vocabulary, 2)
    """
    embedding_matrix = TSNE(n_components=2).fit_transform(embedding_matrix)
    #print(embedding_matrix)
    return embedding_matrix[:, :2]


# ** TASK 5
# This should save a PDF of the embeddings. This is the *only* function marked
# marked with "** TASK" that will NOT be automatically invoked by our grading
# script (it will be "stubbed-out", by monkey-patching). You must run this
# function on your own, save the PDF produced by it, and place it in your
# submission directory with name 'tsne_embeds.pdf'.
def VisualizeTSNE(sess):
    #sess = tf.Session()
    if EMBEDDING_VAR is None:
        print('Cannot visualize embeddings. EMBEDDING_VAR is not set')
        return
    embedding_mat = sess.run(EMBEDDING_VAR)
    tsne_embeddings = ComputeTSNE(embedding_mat)

    class_to_words = {
        'positive': [
                'relaxing', 'upscale', 'luxury', 'luxurious', 'recommend', 'relax',
                'choice', 'best', 'pleasant', 'incredible', 'magnificent', 
                'superb', 'perfect', 'fantastic', 'polite', 'gorgeous', 'beautiful',
                'elegant', 'spacious'
        ],
        'location': [
                'avenue', 'block', 'blocks', 'doorman', 'windows', 'concierge', 'living'
        ],
        'furniture': [
                'bedroom', 'floor', 'table', 'coffee', 'window', 'bathroom', 'bath',
                'pillow', 'couch'
        ],
        'negative': [
                'dirty', 'rude', 'uncomfortable', 'unfortunately', 'ridiculous',
                'disappointment', 'terrible', 'worst', 'mediocre'
        ]
    }

    # TODO(student): Visualize scatter plot of tsne_embeddings, showing only words
    # listed in class_to_words. Words under the same class must be visualized with
    # the same color. Plot both the word text and the tSNE coordinates.

    positive_words=class_to_words['positive']
    location_words=class_to_words['location']
    furniture_words=class_to_words['furniture']
    negative_words=class_to_words['negative']

    
    x = []
    y = []

    for i in positive_words:
        x.append(tsne_embeddings[TERM_INDEX[i]][0])
        y.append(tsne_embeddings[TERM_INDEX[i]][1])
        #if TERM_INDEX.has_key(i):
    x1 = []
    y1 = []

    for i in location_words:
        x1.append(tsne_embeddings[TERM_INDEX[i]][0])
        y1.append(tsne_embeddings[TERM_INDEX[i]][1])        
    
    x2 = []
    y2 = []

    for i in furniture_words:
        x2.append(tsne_embeddings[TERM_INDEX[i]][0])
        y2.append(tsne_embeddings[TERM_INDEX[i]][1])            

    x3 = []
    y3 = []

    for i in negative_words:
        x3.append(tsne_embeddings[TERM_INDEX[i]][0])
        y3.append(tsne_embeddings[TERM_INDEX[i]][1])    



    print('visualization should generate now')


    
    f=plt.figure(figsize=(16, 16)) 

    for i in range(len(x)):
        plt.scatter(x[i],y[i],color='b')
        plt.annotate(positive_words[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')


    for i in range(len(x1)):
        plt.scatter(x1[i],y1[i],color='g')
        plt.annotate(location_words[i],
                     xy=(x1[i], y1[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

    for i in range(len(x2)):
        plt.scatter(x2[i],y2[i],color='r')
        plt.annotate(furniture_words[i],
                     xy=(x2[i], y2[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')    
    for i in range(len(x3)):
        plt.scatter(x3[i],y3[i],color='orange')
        plt.annotate(negative_words[i],
                     xy=(x3[i], y3[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')   
    #plt.show()
    f.savefig("tsne_embeds.pdf", bbox_inches='tight')
    



CACHE = {}
def ReadAndTokenize(filename):
    """return dict containing of terms to frequency."""
    global CACHE
    global VOCABULARY
    if filename in CACHE:
        return CACHE[filename]
    comment = open(filename).read()
    words = Tokenize(comment)

    terms = collections.Counter()
    for w in words:
        VOCABULARY[w] += 1
        terms[w] += 1

    CACHE[filename] = terms
    return terms

TERM_INDEX = None
def MakeDesignMatrix(x):
    global TERM_INDEX
    if TERM_INDEX is None:
        print('Total words: %i' % len(VOCABULARY.values()))
        min_count, max_count = numpy.percentile(list(VOCABULARY.values()), [50.0, 99.8])
        TERM_INDEX = {}
        for term, count in VOCABULARY.items():
            if count > min_count and count <= max_count:
                idx = len(TERM_INDEX)
                TERM_INDEX[term] = idx
    #
    x_matrix = numpy.zeros(shape=[len(x), len(TERM_INDEX)], dtype='float32')
    for i, item in enumerate(x):
        for term, count in item.items():
            if term not in TERM_INDEX:
                continue
            j = TERM_INDEX[term]
            x_matrix[i, j] =     count     # 1.0    # Try count or log(1+count)
    return x_matrix

def GetDataset():
    """Returns numpy arrays of training and testing data."""
    x_train = []
    x_test = []
    y_train = []
    y_test = []

    classes1 = set()
    classes2 = set()
    for f in GetInputFiles():
        class1, class2, fold, fname = f.split('/')[-4:]
        classes1.add(class1)
        classes2.add(class2)
        class1 = class1.split('_')[0]
        class2 = class2.split('_')[0]

        x = ReadAndTokenize(f)
        y = [int(class1 == 'positive'), int(class2 == 'truthful')]
        if fold == 'fold4':
            x_test.append(x)
            y_test.append(y)
        else:
            x_train.append(x)
            y_train.append(y)

    ### Make numpy arrays.
    x_test = MakeDesignMatrix(x_test)
    x_train = MakeDesignMatrix(x_train)
    y_test = numpy.array(y_test, dtype='float32')
    y_train = numpy.array(y_train, dtype='float32')

    dataset = (x_train, y_train, x_test, y_test)
    with open('dataset.pkl', 'wb') as fout:
        pickle.dump(dataset, fout)
    return dataset



def print_f1_measures(probs, y_test):
    y_test[:, 0] == 1    # Positive
    positive = {
            'tp': numpy.sum((probs[:, 0] > 0)[numpy.nonzero(y_test[:, 0] == 1)[0]]),
            'fp': numpy.sum((probs[:, 0] > 0)[numpy.nonzero(y_test[:, 0] == 0)[0]]),
            'fn': numpy.sum((probs[:, 0] <= 0)[numpy.nonzero(y_test[:, 0] == 1)[0]]),
    }
    negative = {
            'tp': numpy.sum((probs[:, 0] <= 0)[numpy.nonzero(y_test[:, 0] == 0)[0]]),
            'fp': numpy.sum((probs[:, 0] <= 0)[numpy.nonzero(y_test[:, 0] == 1)[0]]),
            'fn': numpy.sum((probs[:, 0] > 0)[numpy.nonzero(y_test[:, 0] == 0)[0]]),
    }
    truthful = {
            'tp': numpy.sum((probs[:, 1] > 0)[numpy.nonzero(y_test[:, 1] == 1)[0]]),
            'fp': numpy.sum((probs[:, 1] > 0)[numpy.nonzero(y_test[:, 1] == 0)[0]]),
            'fn': numpy.sum((probs[:, 1] <= 0)[numpy.nonzero(y_test[:, 1] == 1)[0]]),
    }
    deceptive = {
            'tp': numpy.sum((probs[:, 1] <= 0)[numpy.nonzero(y_test[:, 1] == 0)[0]]),
            'fp': numpy.sum((probs[:, 1] <= 0)[numpy.nonzero(y_test[:, 1] == 1)[0]]),
            'fn': numpy.sum((probs[:, 1] > 0)[numpy.nonzero(y_test[:, 1] == 0)[0]]),
    }

    all_f1 = []
    for attribute_name, score in [('truthful', truthful),
                                                                ('deceptive', deceptive),
                                                                ('positive', positive),
                                                                ('negative', negative)]:
        precision = float(score['tp']) / float(score['tp'] + score['fp'])
        recall = float(score['tp']) / float(score['tp'] + score['fn'])
        f1 = 2*precision*recall / (precision + recall)
        all_f1.append(f1)
        print('{0:9} {1:.2f} {2:.2f} {3:.2f}'.format(attribute_name, precision, recall, f1))
    print('Mean F1: {0:.4f}'.format(float(sum(all_f1)) / len(all_f1)))



def BuildInferenceNetwork(x, l2_reg_val, is_training):
    """From a tensor x, runs the neural network forward to compute outputs.
    This essentially instantiates the network and all its parameters.

    Args:
        x: Tensor of shape (batch_size, vocab size) which contains a sparse matrix
             where each row is a training example and containing counts of words
             in the document that are known by the vocabulary.

    Returns:
        Tensor of shape (batch_size, 2) where the 2-columns represent class
        memberships: one column discriminates between (negative and positive) and
        the other discriminates between (deceptive and truthful).
    """
    global EMBEDDING_VAR
    
    
    ## Build layers starting from input.
    net = x
    
    l2_reg = tf.contrib.layers.l2_regularizer(l2_reg_val)

    ## First Layer
    net = FirstLayer(net, l2_reg_val, is_training)
    

    EMBEDDING_VAR=tf.trainable_variables('fully_connected/weights:0')[0]
    #print(EMBEDDING_VAR)

    ## Second Layer.
    net = tf.contrib.layers.fully_connected(
            net, 10, activation_fn=None, weights_regularizer=l2_reg)
    net = tf.contrib.layers.dropout(net, keep_prob=0.5, is_training=is_training)
    net = tf.nn.relu(net)

    net = tf.contrib.layers.fully_connected(
            net, 2, activation_fn=None, weights_regularizer=l2_reg)

    return net



def main(argv):
    ######### Read dataset
    x_train, y_train, x_test, y_test = GetDataset()

    ######### Neural Network Model
    x = tf.placeholder(tf.float32, [None, x_test.shape[1]], name='x')
    y = tf.placeholder(tf.float32, [None, y_test.shape[1]], name='y')
    is_training = tf.placeholder(tf.bool, [])

    l2_reg_val = 1e-6    # Co-efficient for L2 regularization (lambda)
    net = BuildInferenceNetwork(x, l2_reg_val, is_training)


    ######### Loss Function
    tf.losses.sigmoid_cross_entropy(multi_class_labels=y, logits=net)

    ######### Training Algorithm
    learning_rate = tf.placeholder_with_default(
            numpy.array(0.01, dtype='float32'), shape=[], name='learn_rate')
    opt = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    train_op = tf.contrib.training.create_train_op(tf.losses.get_total_loss(), opt)
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())


    def evaluate(batch_x=x_test, batch_y=y_test):
        probs = sess.run(net, {x: batch_x, is_training: False}) 
        print_f1_measures(probs, batch_y)

    def batch_step(batch_x, batch_y, lr):
            sess.run(train_op, {
                    x: batch_x,
                    y: batch_y,
                    is_training: True, learning_rate: lr,
            })

    def step(lr=0.01, batch_size=100):
        indices = numpy.random.permutation(x_train.shape[0])
        for si in range(0, x_train.shape[0], batch_size):
            se = min(si + batch_size, x_train.shape[0])
            slice_x = x_train[indices[si:se]] + 0    # + 0 to copy slice
            slice_x = SparseDropout(slice_x)
            batch_step(slice_x, y_train[indices[si:se]], lr)


    lr = 0.05
    print('Training model ... ')
    for j in range(300): step(lr)
    for j in range(300): step(lr/2)
    for j in range(300): step(lr/4)
    print('Results from training:')
    evaluate()
    #VisualizeTSNE(sess)
    
    



if __name__ == '__main__':
    tf.random.set_random_seed(0)
    main([])
