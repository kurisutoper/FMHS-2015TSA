import Graphics, Core
import sys, imp

if __name__ == '__main__':
  ai_paths = sys.argv[1:]
  ai_list = []
  colors = ['red', 'orange', 'yellow',
            'green', 'blue', 'indigo', 'violet']
  alignment_counter = 0
  for i in ai_paths:
    if i != 'null':
        ai_module = imp.load_source('ShouldntMatter', i)
        ai_list.append(Core.AI(ai_module.decision, i, colors[alignment_counter]))
    alignment_counter += 1
  Graphics.init(sys.argv, ai_list)
