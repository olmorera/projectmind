


```python
import sys
from pathlib import Path


class FileProcessor:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.file_content = None
        self.word_count = None


    def read_file(self) -> str:
        """
        Reads the content of the file at the given input path.


        :return: The content of the file as a string.
        """
        try:
            with open(self.input_path, 'r') as file:
                self.file_content = file.read()
        except FileNotFoundError:
            print(f"File not found at path: {self.input_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

        return self.file_content


    def count_words(self) -> int:
        """
        Counts the number of words in the file content.


        :return: The number of words in the file content.
        """
        if not self.file_content:
            self.file_content = self.read_file()
        self.word_count = len(self.file_content.split())
        return self.word_count


    def save_summary(self, output_path: str) -> None:
        """
        Saves the summary of the word count to the given output path.

        """
        if not self.word_count:
            self.word_count = self.count_words()
        
        try:
            with open(output_path, 'w') as file:
                file.write(f"Word count: {self.word_count}")
        except Exception as e:
            print(f"Error saving summary: {e}")
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python file_processor.py <input_file_path> <output_file_path>")
        sys.exit(1)


    input_path = sys.argv[1]
    output_path = sys.argv[2]


    processor = FileProcessor(input_path)
    processor.count_words()
    processor.save_summary(output_path)

    print(f"Word count saved to {output_path}")


if __name__ == '__main__':
    main()
``` 