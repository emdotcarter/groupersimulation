import numpy as np
import matplotlib.pyplot as plt

debug = 0

displayGraphs = True
saveGraphs = True

simulationsPerFishingPressure = 5
fishingPressures = np.linspace(0.1, 0.5, 5)
graphColors = ['r--', 'b--', 'g--', 'y--', 'k--']

initialPopulationSize = 1000
carryingCapacity = 3000
minimumFishingAge = 3
yearsBeforeFishing = 100

simulationYears = 500


class ProbabilityCache:
    reproductionProbabilitiesByAge = {}
    numberOfOffspringByAge = {}
    mortalityByAge = {}
    sexChangeProbabilityByAge = {}

    def reproductionProbability(age):
        if age not in ProbabilityCache.reproductionProbabilitiesByAge:
            ProbabilityCache.reproductionProbabilitiesByAge[age] = np.exp(-(np.exp(-(-6.42 + 1.81 * age))))

        return ProbabilityCache.reproductionProbabilitiesByAge[age]

    def numberOfOffspring(age):
        if age not in ProbabilityCache.numberOfOffspringByAge:
            ProbabilityCache.numberOfOffspringByAge[age] = int(np.round(25 * ((80.997 * age) - 151.2)))

        return ProbabilityCache.numberOfOffspringByAge[age]

    def mortality(age):
        if age not in ProbabilityCache.mortalityByAge:
            ProbabilityCache.mortalityByAge[age] = (0.4298 / (age ** 0.488))

        return ProbabilityCache.mortalityByAge[age]

    def sexChangeProbability(age):
        if age not in ProbabilityCache.sexChangeProbabilityByAge:
            ProbabilityCache.sexChangeProbabilityByAge[age] = float(1 / (1 + np.exp((age - 10) / 0.367)))

        return ProbabilityCache.sexChangeProbabilityByAge[age]

class Grouper:
    ageOfReproduction = 3

    def __init__(self):
        self.age = 0
        self.sex = 'Female'

    def calculateNumberOfOffspring(self):
        if self.sex == 'Female' and self.age >= Grouper.ageOfReproduction and np.random.random() < ProbabilityCache.reproductionProbability(self.age):
            return ProbabilityCache.numberOfOffspring(self.age)

        return 0

    def incrementAge(self):
        self.age += 1

    def determineAlive(self, fishingPressure = 0):
        return self.age == 0 or np.random.random() > ProbabilityCache.mortality(self.age) + fishingPressure

    def determineSex(self):
        if self.sex == 'Female' and np.random.random() > ProbabilityCache.sexChangeProbability(self.age):
            self.sex = 'Male'

class Simulation:
    def __init__(self, initialPopulationSize, carryingCapacity, fishingPressure, minimumFishingAge, yearsBeforeFishing):
        self.initialPopulationSize = initialPopulationSize
        self.carryingCapacity = carryingCapacity
        self.fishingPressure = fishingPressure
        self.minimumFishingAge = minimumFishingAge
        self.yearsBeforeFishing = yearsBeforeFishing

        self.fishes = [Grouper() for i in range(initialPopulationSize)]

        self.simulationPopulationSizes = []
        self.simulationSexRatios = []

    def run(self, years):
        for year in range(years):
            survivingFishes = []
            survivingMalesOfReproductionAgeCount = 0
            survivingFemalesOfReproductionAgeCount = 0
            potentialNewFishesCount = 0

            for fish in self.fishes:
                if fish.age > self.minimumFishingAge and year >= self.yearsBeforeFishing:
                    fishAlive = fish.determineAlive(self.fishingPressure)
                else:
                    fishAlive = fish.determineAlive()

                if fishAlive:
                    survivingFishes += [fish]
                    fish.determineSex()

                    if fish.sex == 'Female':
                        survivingFemalesOfReproductionAgeCount += 1
                        potentialNewFishesCount += fish.calculateNumberOfOffspring()
                    else:
                        survivingMalesOfReproductionAgeCount += 1

                    fish.incrementAge()

            if debug > 0:
                print('\n\nYear %d:\n' % (year))
                print('len(survivingFishes): %d' % (len(survivingFishes)))
                print('survivingFemalesOfReproductionAgeCount: %d' % (survivingFemalesOfReproductionAgeCount))
                print('survivingMalesOfReproductionAgeCount: %d' % (survivingMalesOfReproductionAgeCount))
                print('potentialNewFishesCount: %d' % (potentialNewFishesCount))

            self.fishes = survivingFishes

            sexRatioOfReproducingFishes = 0
            if survivingFemalesOfReproductionAgeCount > 0:
                sexRatioOfReproducingFishes = float(survivingMalesOfReproductionAgeCount) / survivingFemalesOfReproductionAgeCount

            if len(self.fishes) < self.carryingCapacity:
                fertilityRate = 0.8 * (1 - np.exp(-80 * sexRatioOfReproducingFishes))
                newFishesByFertilityRate = int(np.round(potentialNewFishesCount * fertilityRate))
                newFishesByLarvalMortality = newFishesByFertilityRate * 0.1 * (np.random.gamma(0.5265, 1.8828) / 8)
                newFishesByDensityDependence = int(np.round(newFishesByLarvalMortality / (1 + 2 * np.power((newFishesByLarvalMortality / self.carryingCapacity), 2))))

                if debug > 0:
                    print('newFishesByDensityDependence: %d' % (newFishesByDensityDependence))

                self.fishes += [Grouper() for i in range(newFishesByDensityDependence)]

            self.simulationPopulationSizes += [len(self.fishes)]
            self.simulationSexRatios += [sexRatioOfReproducingFishes]

if displayGraphs:
    populationSizeFigure = plt.subplot(1, 2, 1)
    plt.xlabel('Years')
    plt.ylabel('Population Size')

    sexRatioFigure = plt.subplot(1, 2, 2)
    plt.xlabel('Years')
    plt.ylabel('Sex Ratios')

for fishingPressureIndex in range(len(fishingPressures)):
    fishingPressure = np.round(fishingPressures[fishingPressureIndex], decimals=1)
    graphColor = graphColors[fishingPressureIndex]

    for simNumber in range(simulationsPerFishingPressure):
        sim = Simulation(initialPopulationSize, carryingCapacity, fishingPressure, minimumFishingAge, yearsBeforeFishing)
        sim.run(simulationYears)

        if displayGraphs:
            label = ''
            if simNumber == 0:
                label = fishingPressure

            populationSizeFigure.plot(sim.simulationPopulationSizes, graphColor, label=label)
            sexRatioFigure.plot(sim.simulationSexRatios, graphColor, label=label)

if displayGraphs:
    populationSizeFigure.legend()
    sexRatioFigure.legend()
    plt.show()

if saveGraphs:
    plt.savefig('population_simulation.png', dpi=300)
