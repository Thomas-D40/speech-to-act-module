/**
 * Sample French nursery utterances for testing
 * STT only provides raw text - semantic normalization does the rest
 */

export const SAMPLE_UTTERANCES: string[] = [
  // MEAL - half consumed (different phrasings)
  "Lucas a mangé la moitié de son plat",
  "Lucas a pris la moitié de son assiette",
  "Lucas n'a mangé que 50% de son repas",

  // MEAL - all consumed
  "Emma a tout fini son dessert",
  "Emma a terminé son dessert complètement",
  "L'assiette de dessert d'Emma est vide",

  // MEAL - nothing consumed
  "Paul n'a rien mangé",
  "Paul a refusé de manger",
  "Paul n'a pas touché à son assiette",

  // MEAL - three quarters
  "Nathan a mangé les trois quarts de son repas",
  "Nathan a presque tout fini",

  // MEAL - multiple children
  "Léa et Hugo ont tout fini leur assiette",

  // SLEEP - nap started
  "Louis s'est endormi pour la sieste",
  "Louis fait dodo",
  "Louis dort maintenant",

  // SLEEP - wake up
  "Manon vient de se réveiller",
  "Manon est réveillée",
  "La sieste de Manon est terminée",

  // DIAPER - wet
  "changement de couche mouillée pour Zoé",
  "Zoé a fait pipi",

  // DIAPER - dirty
  "couche sale pour Tom",
  "Tom a fait caca",
  "Tom a fait ses besoins",

  // MOOD - happy
  "Gabriel est très content aujourd'hui",
  "Gabriel est de bonne humeur",
  "Gabriel sourit beaucoup",

  // MOOD - crying
  "Inès pleure beaucoup ce matin",
  "Inès est en pleurs",

  // MOOD - grumpy
  "Mathis est un peu grognon",
  "Mathis râle un peu",

  // ACTIVITIES - outdoor
  "Clara a joué dans le jardin",
  "Clara a joué dehors",

  // ACTIVITIES - arts
  "Ethan a fait de la peinture",
  "Ethan a fait du coloriage",

  // ACTIVITIES - multiple children
  "Jules et Lina ont joué ensemble dehors",
];

export function getRandomUtterance(): string {
  return SAMPLE_UTTERANCES[Math.floor(Math.random() * SAMPLE_UTTERANCES.length)];
}
