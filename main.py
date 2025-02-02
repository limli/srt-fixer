def read_srt(text_file):
    lines = text_file.readlines() if hasattr(text_file, 'readlines') else text_file.splitlines()

    srt_block = {} # index, start, end, text
    state = "start" # start -> times -> text --> start
    for line in lines:
        line = line.strip()
        if state == "start":
            if line == "":
                continue
            elif line.startswith("("):
                continue
            else:
                srt_block['index'] = line
                state = "times"
        elif state == "times":
            try:
                times = line.split(' --> ')
                start_time = times[0]
                end_time = times[1]
            except IndexError as e:
                raise ValueError("times: {}, line: {}, error: {}".format(times, line, e))
            srt_block['start'] = start_time
            srt_block['end'] = end_time
            state = "text"
        elif state == "text" and len(line) > 0:
            if srt_block.get('text', False):
                srt_block['text'] += "\n"
                srt_block['text'] += line
            else:
                srt_block['text'] = line
        elif state == "text" and line == "":
            if 'text' in srt_block:
                yield srt_block
            srt_block = {}
            state = "start"
        else:
            raise ValueError("Error while parsing srt input.")
    return


def is_collision(block, other_block):
    return other_block['start'] < block['end']

def expand_block(block, other_block):
    if not block:
        return other_block

    if block['text'].endswith(other_block['text']):
        text = block['text']
    else:
        text = "{}\n{}".format(block['text'], other_block['text'])

    return {
        'index': block['index'],
        'start': block['start'],
        'end': other_block['end'],
        'text': text,
    }

def merge_overlapping(srt_blocks):
    last_block = None
    for block in srt_blocks:
        if not last_block: # first iteration
            last_block = block
        elif is_collision(last_block, block):
            last_block = expand_block(last_block, block)
        else:
            yield last_block
            last_block = block
    yield last_block

def print_srt_block(srt_block, index=None):
    return "{}\n{} --> {}\n{}\n".format(index or srt_block['index'], srt_block['start'], srt_block['end'], srt_block['text'])

def print_as_srt(srt_blocks):
    index = 0
    for block in srt_blocks:
        index += 1
        print(print_srt_block(block, index))

def export_as_srt(srt_blocks, output):
    index = 0
    new_srt_file = open(output, "w")
    for block in srt_blocks:
        index += 1
        new_srt_file.write(print_srt_block(block, index))
        new_srt_file.write("\n")
    
    new_srt_file.close

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fix overlaping timestamps in SRT files by merging them.')
    parser.add_argument('input', help='The input file.')
    parser.add_argument('-o', help='Define a output file. If no file is given text will be printed to console.')
    args = parser.parse_args()

    try:
        text = open(args.input, "r")
    except IOError:
        raise ValueError("{} is no file.".format(args.input))

    with text:
        srt_blocks = read_srt(text)
        merged = merge_overlapping(srt_blocks)
        if args.o is None:
            print_as_srt(merged)
        else:
            export_as_srt(merged, args.o)

if __name__ == '__main__':
    main()