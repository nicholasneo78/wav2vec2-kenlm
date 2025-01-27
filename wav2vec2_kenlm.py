
"""
    @author
          ______         _                  _
         |  ____|       (_)           /\   | |
         | |__ __ _ _ __ _ ___       /  \  | | __ _ ___ _ __ ___   __ _ _ __ _   _
         |  __/ _` | '__| / __|     / /\ \ | |/ _` / __| '_ ` _ \ / _` | '__| | | |
         | | | (_| | |  | \__ \    / ____ \| | (_| \__ \ | | | | | (_| | |  | |_| |
         |_|  \__,_|_|  |_|___/   /_/    \_\_|\__,_|___/_| |_| |_|\__,_|_|   \__, |
                                                                              __/ |
                                                                             |___/
            Email: farisalasmary@gmail.com
            Date:  Sep 15, 2021
"""

"""
This code uses some of the works in the following repos:
https://github.com/parlance/ctcdecode
https://github.com/SeanNaren/deepspeech.pytorch
https://github.com/Wikidepia/wav2vec2-indonesian/blob/master/notebooks/kenlm-wav2vec2.ipynb
"""

from decoder import *
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, Wav2Vec2CTCTokenizer
import utils


device = 'cuda' if torch.cuda.is_available() else 'cpu'

print(f'Device: {device}')

MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-english"
#MODEL_ID = "facebook/wav2vec2-base-10k-voxpopuli-ft-en"

print(f'Loading Wav2Vec2CTC Model: "{MODEL_ID}"')
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

### DEBUG ###
print(type(processor))
print()
print(type(model))
print()
print(processor)
print()
print(model)
###

vocab_dict = processor.tokenizer.get_vocab()
sort_vocab = sorted((value, key) for (key,value) in vocab_dict.items())

print(sort_vocab)

# Lower case ALL letters
vocab = []
for _, token in sort_vocab:
    vocab.append(token.lower())

# replace the word delimiter with a white space since the white space is used by the decoders
vocab[vocab.index(processor.tokenizer.word_delimiter_token)] = ' '

# you can download the following ARPA LM from this link:
# "https://kaldi-asr.org/models/5/4gram_big.arpa.gz"
lm_path = "lm/4gram_big.arpa.gz" 

# alpha, beta, and beam_wdith SHOULD be tuned on the dev-set to get the best settings
# Feel free to check other inputs of the BeamCTCDecoder
alpha=0
beta=0
beam_width = 1024

beam_decoder = BeamCTCDecoder(vocab, lm_path=lm_path,
                                 alpha=alpha, beta=beta,
                                 cutoff_top_n=40, cutoff_prob=1.0,
                                 beam_width=beam_width, num_processes=16,
                                 blank_index=vocab.index(processor.tokenizer.pad_token))


greedy_decoder = GreedyDecoder(vocab, blank_index=vocab.index(processor.tokenizer.pad_token))


# load the test audio file
# NOTE: we are loading the same file multiple times to simulate batch processing.
# Hence, you can assign a list of paths to different audio files of your choice and test the feature.
#audio_files_paths = ['english_sample.wav'] * 2
audio_files_paths = ['84-121123-0001.flac', '84-121123-0002.flac', '10993-2114000-0001.flac', '10993-2114000-0002.flac']

print(f'Load audio files: "{audio_files_paths}"')
batch_audio_files, sampling_rate = utils.load_audio_files(audio_files_paths)

print('Get logits from the Wav2Vec2ForCTC model....')
logits, max_signal_length = utils.get_logits(batch_audio_files, model, processor, device)

print('Decoding using the Beam Search Decoder....')
beam_decoded_output, beam_decoded_offsets = beam_decoder.decode(logits)

print('Decoding using the Greedy Decoder....')
greedy_decoded_output, greedy_decoded_offsets = greedy_decoder.decode(logits)


print('Printing the output of the first audio file...\n')

print('Greedy Decoding Output:', greedy_decoded_output[1][0])
print()
print('#'*85)
print()
print('Beam Search Decoding Output:', beam_decoded_output[1][0]) # print the top prediction of the beam search

print('Compute Segments....')
batch_segments_list_greedy = utils.get_segments(logits, greedy_decoded_output, max_signal_length, sampling_rate, vocab)
batch_segments_list_beam = utils.get_segments(logits, beam_decoded_output, max_signal_length, sampling_rate, vocab)

print('Printing the first segment (word) of the first audio file...')
print()
print('#'*85)
print()
print('Greedy Decoding Output:', batch_segments_list_greedy[1][0])
print()
print('Beam Search Decoding Output:', batch_segments_list_beam[1][0])

print('Done!!')


