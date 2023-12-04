from matplotlib import pyplot as plt
from scipy import stats

# Plots residuals
def plot_residuals(x, y, x_label, title, fit):
    residuals = y - (fit.slope*x + fit.intercept)
    plt.hist(residuals)

    plt.title("Frequency of " + x_label.title())
    plt.xlabel(x_label.title)
    plt.ylabel("Frequency")
    plt.savefig("output_plots/"+"_".join(title.split())+"_residuals")
    plt.clf()

# Plots data with optional best fit line
def plot(x, y, x_label, y_label, title):
    
    plt.plot(x, y, 'b.', alpha=0.5)

    # Linear regression
    fit = stats.linregress(x,y)
    prediction = x.apply(lambda x : x*fit.slope + fit.intercept)
    plt.plot(x, prediction, 'r-', linewidth=3)

    # Format
    plt.title(title.title())
    plt.xlabel(x_label.title())
    plt.ylabel(y_label.title())
    plt.savefig("output_plots/"+"_".join(title.split()))
    plt.clf()

    # Residuals
    plot_residuals(x, y, y_label, title, fit)

OUTPUT_TEMPLATE = (
    "{title}\n"
    "Slope: {slope:.3g}\n"
    "Slope p-value: {p_value:.3g}\n"
    "Equal variance p-value: {equal_variance_p:.3g}\n"
    "Residuals normality p-values: {residuals_normality_p:.3g}\n"
    "Number of data points: {n:.3g}\n"
)

def print_fit(x, y, title):
    fit = stats.linregress(x,y)
    residuals = y - (fit.slope*x + fit.intercept)
    print(OUTPUT_TEMPLATE.format(
        title=title.upper(),
        slope=fit.slope,
        p_value=fit.pvalue,
        equal_variance_p=stats.levene(x,y).pvalue,
        residuals_normality_p=stats.normaltest(residuals).pvalue,
        n=len(x)
    ))