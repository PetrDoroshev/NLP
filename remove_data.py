import shutil
import os

def mod_remove_data(elements_to_save, additional_conf=True):

    if additional_conf:
        print("Will be deleted")
        for key, val in elements_to_save.items():
            if val is None:
                continue
            else:
                print(f"{key}: {val} ALL CONTENT INSIDE WILL BE DELETED!")
        ans = input("'y' to delete:")
        if ans != 'y':
            print("Aborting...")
            return
        else:
            print("Deleting...")
    
    if elements_to_save["articles"] is not None:
        shutil.rmtree(elements_to_save["articles"])
        os.mkdir(elements_to_save["articles"])

    if elements_to_save["raw_parags"] is not None:
        shutil.rmtree(elements_to_save["raw_parags"])
        os.mkdir(elements_to_save["raw_parags"])
        
    if elements_to_save["images"] is not None:
        shutil.rmtree(elements_to_save["images"])
        os.mkdir(elements_to_save["images"])
    
    if elements_to_save["fragments"] is not None:
        shutil.rmtree(elements_to_save["fragments"])
        os.mkdir(elements_to_save["fragments"])
    
    if elements_to_save["clean_fragments"] is not None:
        shutil.rmtree(elements_to_save["clean_fragments"])
        os.mkdir(elements_to_save["clean_fragments"])
    
    if elements_to_save["tokens"] is not None:
        shutil.rmtree(elements_to_save["tokens"])
        os.mkdir(elements_to_save["tokens"])
    
    if elements_to_save["lemmas"] is not None:
        shutil.rmtree(elements_to_save["lemmas"])
        os.mkdir(elements_to_save["lemmas"])
    
    if elements_to_save["word2vec_model"] is not None:
        os.remove(elements_to_save["word2vec_model"])
    
    if elements_to_save["func_triplets"] is not None:
        os.remove(elements_to_save["func_triplets"])
    
    if elements_to_save["hier_triplets"] is not None:
        os.remove(elements_to_save["hier_triplets"])