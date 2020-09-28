import re


class CleanupScrapedJaapDataPipeline:
    def process_item(self, item, spider):
        for k, v in item.items():
            if isinstance(v, dict):
                v = self.process_item(v, spider)
            elif isinstance(v, (str, bytes)):
                v = re.sub('€\s+', '', v)  # Remove € sign and space after.
                v = re.sub('\s+k\.k\.', '', v)  # Remove k.k. and space before.
                v = re.sub('\\r\\n', '', v)  # Remove \r\n.
                v = re.sub('\s+', ' ', v)  # Remove duplicate whitespaces.
                v = re.sub('house_result_', '', v)  # Remove house_result_ prefix from id.
                v = v.rstrip()  # Strip trailing space.
                v = v.lstrip()  # Strip leading space.

            item[k] = v  # Replace value of k.

        return item
